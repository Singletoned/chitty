#!/usr/bin/env python3
"""Retro numbers for repositories that use Chitty, with no LLM involved.

    python3 scripts/retro.py REPO [REPO ...]

For each repository, by ISO week: reviews passed and failed (from ticket
history), how often tickets pass their first review with and without a cold
read, `chitty run` sessions and hours (from the machine-local usage log), and
the share of commits that are Chitty autocommits. Then failure causes and the
tickets that failed review most often.

Tickets written before Chitty kept history have no dated reviews; their
verdicts still count in the cause and first-review figures, dated by creation.
"""

import collections
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass

TOP_FAILING_TICKETS = 5

TICKET_GLOB = "chitty/**/[A-Z]*-[0-9]*--*.md"
TRANSITION = re.compile(r"^- (\d{4}-\d\d-\d\d)\S* \S+ (\S+) → (\S+)$", re.MULTILINE)
VERDICT = re.compile(r"^(?:Reviewed:|Review failed \(([a-z]+)[^)]*\))", re.MULTILINE)
COLD_READ_NOTE = re.compile(r"^cold read", re.IGNORECASE | re.MULTILINE)
CREATED = re.compile(r"^created: (\d{4}-\d\d-\d\d)", re.MULTILINE)
FAILED_REVIEW_TARGETS = {"doing", "to-plan", "planning", "blocked", "error"}


@dataclass(frozen=True)
class Ticket:
    name: str
    created: str
    reviews: tuple[tuple[str, bool], ...]
    """(date, passed) for each transition out of review, in order."""
    failure_causes: tuple[str, ...]
    first_verdict_passed: bool | None
    cold_read: bool


def week(date: str) -> str:
    year, number, _ = datetime.date.fromisoformat(date[:10]).isocalendar()
    return f"{year}-W{number:02d}"


def parse_ticket(name: str, text: str) -> Ticket:
    created = CREATED.search(text)
    if created is None:
        raise ValueError(f"{name}: no `created:` date in frontmatter")
    reviews = tuple(
        (date, new == "done")
        for date, old, new in TRANSITION.findall(text)
        if old == "review" and (new == "done" or new in FAILED_REVIEW_TARGETS)
    )
    verdicts = [match.group(1) for match in VERDICT.finditer(text)]
    return Ticket(
        name=name,
        created=created.group(1),
        reviews=reviews,
        failure_causes=tuple(cause for cause in verdicts if cause is not None),
        first_verdict_passed=(verdicts[0] is None) if verdicts else None,
        cold_read=bool(COLD_READ_NOTE.search(text)) or "→ cold-read" in text,
    )


def ticket_weeks(tickets: list[Ticket]) -> dict[str, collections.Counter]:
    weeks: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for ticket in tickets:
        for date, passed in ticket.reviews:
            weeks[week(date)]["review pass" if passed else "review fail"] += 1
        if ticket.first_verdict_passed is not None:
            when = ticket.reviews[0][0] if ticket.reviews else ticket.created
            kind = "cold" if ticket.cold_read else "plain"
            weeks[week(when)][f"{kind} tickets"] += 1
            weeks[week(when)][f"{kind} first pass"] += ticket.first_verdict_passed
    return weeks


def usage_weeks(records: list[dict]) -> dict[str, collections.Counter]:
    weeks: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for record in records:
        counts = weeks[week(record["started"])]
        counts["sessions"] += 1
        counts["seconds"] += record["seconds"]
        counts["errors"] += record.get("status_after") == "error"
    return weeks


def commit_weeks(log_lines: list[str]) -> dict[str, collections.Counter]:
    weeks: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for line in log_lines:
        date, _, subject = line.partition(" ")
        weeks[week(date)]["commits"] += 1
        weeks[week(date)]["chitty commits"] += subject.startswith("chitty: ")
    return weeks


def percent(part: int, whole: int) -> str:
    return f"{part / whole:.0%}" if whole else "-"


def week_table(tickets: dict, usage: dict, commits: dict) -> list[str]:
    rows = [
        (
            "| Week | Reviews pass/fail | First pass: cold | First pass: none "
            "| Runner sessions | Runner hours | Errors | Commits | Chitty commits |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    active = {key for key, counts in commits.items() if counts["chitty commits"]}
    for key in sorted(set(tickets) | set(usage) | active):
        t, u, c = tickets.get(key, {}), usage.get(key, {}), commits.get(key, {})
        rows.append(
            f"| {key} | {t.get('review pass', 0)}/{t.get('review fail', 0)} "
            f"| {percent(t.get('cold first pass', 0), t.get('cold tickets', 0))}"
            f" of {t.get('cold tickets', 0)} "
            f"| {percent(t.get('plain first pass', 0), t.get('plain tickets', 0))}"
            f" of {t.get('plain tickets', 0)} "
            f"| {u.get('sessions', 0)} | {u.get('seconds', 0) / 3600:.1f} | {u.get('errors', 0)} "
            f"| {c.get('commits', 0)} "
            f"| {percent(c.get('chitty commits', 0), c.get('commits', 0))} |"
        )
    return rows


def failure_lines(tickets: list[Ticket]) -> list[str]:
    causes = collections.Counter(cause for ticket in tickets for cause in ticket.failure_causes)
    lines = ["Failed reviews by cause: " + ", ".join(f"{c} {n}" for c, n in causes.most_common())]
    worst = sorted(tickets, key=lambda ticket: len(ticket.failure_causes), reverse=True)
    lines.append("Most failed reviews:")
    lines += [
        f"- {len(ticket.failure_causes)} {ticket.name}"
        for ticket in worst[:TOP_FAILING_TICKETS]
        if ticket.failure_causes
    ]
    return lines


def usage_records(project: str) -> list[dict]:
    base = pathlib.Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser()
    path = base / "chitty" / "usage" / f"{project}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def report(repo: pathlib.Path) -> list[str]:
    project = tomllib.loads((repo / "chitty.toml").read_text())["project"]
    tickets = [
        parse_ticket(path.stem.split("--")[0], path.read_text())
        for path in sorted(repo.glob(TICKET_GLOB))
    ]
    log = subprocess.run(
        ["git", "log", "--format=%ad %s", "--date=short"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return [
        f"## {project}",
        "",
        *week_table(ticket_weeks(tickets), usage_weeks(usage_records(project)), commit_weeks(log)),
        "",
        *failure_lines(tickets),
    ]


def main(arguments: list[str]) -> None:
    if not arguments:
        sys.exit("usage: retro.py REPO [REPO ...]")
    for repo in arguments:
        print("\n".join(report(pathlib.Path(repo))), end="\n\n")


if __name__ == "__main__":
    main(sys.argv[1:])
