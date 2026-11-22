---
title: Add `chitty summary` to show what changed in recent hours
status: cold-read
priority: high
created: 2026-11-22
---

## Description

Requested by the person on 2026-11-21: "chitty needs a summary feature, where I can see what has happened in the last few hours", and again on 2026-11-22.

Today, answering "what happened since this morning?" means piecing together `git log` on `main`, each ticket's `## History` lines, runner output and notes. The data is already there: every status change is a timestamped History line naming the actor (`HISTORY_LINE_RE` in `src/chitty/model.py`, for example `- 2026-11-22T22:16:03Z zesty-ochre-heron doing → planning`).

Decisions:

- New `Task.timed_transitions() -> list[tuple[datetime, str | None, str]]` in `src/chitty/model.py`, next to `transitions()`: the `(UTC timestamp, old, new)` of each History line matching `HISTORY_LINE_RE` with its `timestamp` group, in file order. Date-only lines (the `date` alternative, old format) are skipped, never coerced to a time.
- New `summary_sections(tasks: Sequence[StoredTask], now: datetime, hours: int) -> list[tuple[str, list[SummaryLine]]]` in `src/chitty/store.py`, pure (no Git, no files). `SummaryLine` is a frozen dataclass with `id: TaskId`, `title: str`, `when: datetime`, `actor: str` and `new: bool`. For each task, keep the timed transitions with `now - timedelta(hours=hours) <= when <= now` (a transition after `now`, from clock skew, is left out); a task with none is left out. Its last transition is the one with the greatest timestamp, the later line on a tie; the task goes in the section named by that transition's new status, with `when` and `actor` from it. `new` is true when the task's earliest timed transition (smallest timestamp, the earlier line on a tie) has no old status and is in the window. Sections are ordered by the reverse of `STATUSES` (so `done` first), then any other status names, sorted; empty sections are left out. Within a section, lines are ordered by `when`, newest first, then by id.
- New command `chitty summary [--hours N]`: `N` is a `click.IntRange(1, SUMMARY_MAX_HOURS)`, default `SUMMARY_HOURS` (24); both module-level constants in `src/chitty/cli.py`, `SUMMARY_MAX_HOURS = 8784` (366 days). It calls `summary_sections(repo.all_tasks(), datetime.now(UTC), N)` (every context, active and archived, from each ticket's authoritative copy, so a ticket being worked shows its branch copy) and prints, with one blank line between sections, a header `<status> (<count>)` per section, then per line two spaces, the id, two spaces, the title with ` (new)` appended when `new`, two spaces, `when` as `HH:MM` UTC, a space and the actor. With no sections it prints `nothing changed in the last <N> hours` (always `hours`, even for 1) and exits 0.
- `cli.py` only parses, calls and prints, as `AGENTS.md` asks.

Out of scope: MCP, commits and `Task:` trailers, notes, a `--since` time, and any colour or glyphs.

Tests, in a new `tests/test_summary.py`. Build `StoredTask`s directly (`StoredTask(id, "tasks", Path("chitty/tasks/x.md"), False, chitty.model.parse(text))`) from ticket text with a `## History` section, and use a fixed `now = datetime(2026, 11, 22, 12, 0, tzinfo=UTC)`.

- Examples for `summary_sections`: a ticket moved `todo → doing → review → done` inside the window appears only under `done`; a ticket whose only transition is 25 hours old is absent with `hours=24` and present with `hours=48`; a ticket created inside the window has `new` true, one created before it false; two tickets in one section are ordered newest first, and two with the same `when` by id; a date-only History line dated `2026-11-22` (which midnight coercion would put inside the window) contributes nothing; a transition to an unknown status `zzz` gets its own section after the `STATUSES` ones; a transition one minute after `now` is left out; a History event line (`- <timestamp> tester: changed notes`) between two transitions is ignored; nothing in the window gives `[]`. One direct example for `Task.timed_transitions`: a History with a date-only line, an event line and two timed transitions returns just the two, in file order, as UTC datetimes.
- Property, with Hypothesis (`max_examples=examples(50)` from `tests/__init__.py`): draw one to six tickets, each with one to five transitions whose new statuses are drawn from `STATUSES` and whose times are drawn as whole seconds, sorted ascending (ties allowed), within 72 hours before `now`, with `now - hours` itself drawn sometimes (`st.one_of` with that exact value), and a drawn `hours` from 1 to 72. Every ticket with a transition at or after `now - hours` appears exactly once, in the section of its latest such transition; no other ticket appears; within each section `when` is non-increasing; `new` is true exactly when the ticket's earliest transition has no old status and is in the window. "Latest" and "earliest" break ties by line order, as above.
- CLI: in a `RepoTestCase` repository (context `tasks`), write `chitty/tasks/TASK-1--one.md` (title `One`, History: created `todo` 2 hours ago, then `todo → done` 1 hour ago), `TASK-2--two.md` (title `Two`, created `todo` 10 hours ago) and `TASK-3--three.md` (title `Three`, created `todo` 30 hours ago), all by actor `tester`, with timestamps computed from `datetime.now(UTC)` and rounded to the second. Run `chitty summary` and `chitty summary --hours 48` through `click.testing.CliRunner` with `chitty.cli.cli`, and assert the exact output, computing the `HH:MM` parts from the same timestamps. Also `--hours 0` and `--hours x` exit 2.

To show the tests fail first, commit a stub first (`timed_transitions` returning `[]`, `summary_sections` returning `[]`, and a `summary` command printing nothing), run the tests against it, and record the assertion failures in a note; an import error does not count.

## Acceptance Criteria

- [ ] The `summary_sections` examples, the property and the CLI test in `tests/test_summary.py` pass, and fail before the change; record both runs in a note
- [ ] `chitty --help` lists `summary`; `make check` passes

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:32Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
- 2026-11-22T22:50:39Z plucky-umber-wren: changed title, priority, description, acceptance criteria
- 2026-11-22T22:50:39Z plucky-umber-wren backlog → cold-read
- 2026-11-22T22:52:32Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:53:42Z plucky-umber-wren: changed description
