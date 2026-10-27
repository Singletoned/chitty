"""Pure conversion of one legacy Backlog.md task file."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml

from chitty.model import DESCRIPTION, NOTES, PLAN, SUMMARY, Task, new_task

STATUS = {"To Do": "todo", "In Progress": "doing", "Done": "done"}
SECTIONS = {
    "Description": DESCRIPTION,
    "Implementation Plan": PLAN,
    "Implementation Notes": NOTES,
    "Final Summary": SUMMARY,
    "Comments": NOTES,
}
MARKER = re.compile(r"<!-- (?:SECTION:[A-Z_]+:(?:BEGIN|END)|AC:(?:BEGIN|END)) -->\n?")
HEADING = re.compile(r"^## (.+)$", re.MULTILINE)
CRITERION = re.compile(r"^- \[([ xX])\] (?:#\d+ )?(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class ConvertedTask:
    old_id: str
    task: Task
    reports: tuple[str, ...]


def convert(path: Path) -> ConvertedTask:
    """Map one legacy task without allocating an ID or writing a file."""
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    _, raw, body = text.split("---\n", 2)
    loaded = yaml.safe_load(raw)
    if not isinstance(loaded, Mapping):
        raise TypeError(f"{path}: frontmatter must be a mapping")
    fields = cast(Mapping[str, Any], loaded)
    old_id = str(fields["id"])
    status = str(fields.get("status", "Draft"))
    reports: list[str] = []
    mapped_status = STATUS.get(status, "backlog")
    notes: list[str] = []
    if mapped_status == "backlog":
        reports.append(f"{old_id}: unknown status {status!r}")
        notes.append(f"Backlog.md status: {status}")
    sections = _sections(body, old_id, reports)
    descriptions = sections.pop(DESCRIPTION, "Imported from Backlog.md.")
    for key, heading in (("references", "References"), ("modified_files", "Modified files")):
        values = list(fields.get(key) or [])
        if values:
            descriptions += f"\n\n### {heading}\n\n" + "\n".join(f"- {value}" for value in values)
    criteria = [text for _, text in CRITERION.findall(body)]
    task = new_task(
        str(fields["title"]),
        date.fromisoformat(str(fields["created_date"])[:10]),
        descriptions,
        criteria,
        {
            "status": mapped_status,
            "labels": list(fields.get("labels") or []),
            "priority": fields.get("priority"),
            "owner": (fields.get("assignee") or [None])[0],
            "depends_on": list(fields.get("dependencies") or []),
        },
    )
    checked = [
        index + 1 for index, (mark, _) in enumerate(CRITERION.findall(body)) if mark.lower() == "x"
    ]
    task = task.with_criteria((), (), checked, ())
    for name, content in sections.items():
        task = task.with_section(name, content)
    for note in notes:
        task = task.with_note(note)
    return ConvertedTask(old_id, task, tuple(reports))


def _sections(body: str, old_id: str, reports: list[str]) -> dict[str, str]:
    cleaned = MARKER.sub("", body).strip()
    matches = list(HEADING.finditer(cleaned))
    result: dict[str, str] = {}
    current = DESCRIPTION
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(cleaned)
        content = cleaned[match.end() : end].strip()
        heading = match.group(1)
        if heading == "Acceptance Criteria":
            continue
        target = SECTIONS.get(heading)
        if target is None:
            reports.append(f"{old_id}: demoted heading {heading!r}")
            result[current] = (result.get(current, "") + f"\n\n### {heading}\n\n{content}").strip()
            continue
        current = target
        separator = "\n\n" if result.get(target) else ""
        result[target] = (result.get(target, "") + separator + content).strip()
    return result
