"""Pure conversion of one legacy Backlog.md task file."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml

from chitty import ids
from chitty.model import DESCRIPTION, NOTES, PLAN, SECTION_ORDER, SUMMARY, Task, new_task

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


@dataclass(frozen=True)
class RenumberedTask:
    old_id: str
    new_id: str
    task: Task
    reports: tuple[str, ...]


def convert(path: Path, *, draft: bool = False) -> ConvertedTask:
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
    mapped_status = "backlog" if draft else STATUS.get(status, "backlog")
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


def renumber(tasks: list[ConvertedTask], prefix: str) -> list[RenumberedTask]:
    """Give subtasks flat IDs, rewrite known references, and preserve provenance."""
    numbers = {
        int(match.group(1)) for item in tasks if (match := re.fullmatch(r"TASK-(\d+)", item.old_id))
    }
    next_number = max(numbers, default=0) + 1
    mapping: dict[str, str] = {}
    parents: dict[str, str] = {}
    for item in tasks:
        match = re.fullmatch(r"TASK-(\d+)(?:\.(\d+))?", item.old_id)
        if match is None:
            raise ValueError(f"unsupported Backlog.md ID {item.old_id!r}")
        number, subtask = match.groups()
        if subtask is None:
            mapping[item.old_id] = f"{prefix}-{number}"
        else:
            mapping[item.old_id] = f"{prefix}-{next_number}"
            parents[item.old_id] = f"{prefix}-{number}"
            next_number += 1
    return [_renumber(item, mapping, parents) for item in tasks]


def _renumber(
    item: ConvertedTask, mapping: Mapping[str, str], parents: Mapping[str, str]
) -> RenumberedTask:
    reports = list(item.reports)
    task = item.task
    dependencies = [
        _rewrite(value, mapping, reports, item.old_id) for value in task.frontmatter.depends_on
    ]
    task = task.with_field("depends_on", dependencies)
    if item.old_id in parents:
        task = task.with_field("parent", parents[item.old_id])
    for section in SECTION_ORDER:
        if section == "Acceptance Criteria":
            continue
        content = task.section(section)
        if content:
            task = task.with_section(section, _rewrite(content, mapping, reports, item.old_id))
    task = task.with_note(f"Backlog.md ID: {item.old_id}")
    return RenumberedTask(item.old_id, mapping[item.old_id], task, tuple(reports))


def _rewrite(value: str, mapping: Mapping[str, str], reports: list[str], old_id: str) -> str:
    def replace(match: re.Match[str]) -> str:
        reference = match.group()
        if reference not in mapping:
            reports.append(f"{old_id}: reference to unknown ID {reference}")
            return reference
        return mapping[reference]

    return re.sub(r"\bTASK-\d+(?:\.\d+)?\b", replace, value)


def import_directory(source: Path, destination: Path, prefix: str, archive: str) -> list[str]:
    """Convert a legacy backlog after all source files parse successfully."""
    locations = (
        ("tasks", False, False),
        ("drafts", True, False),
        ("completed", False, True),
        ("archive", False, True),
    )
    converted: list[ConvertedTask] = []
    reports: list[str] = []
    for name, draft, archived in locations:
        directory = source / name
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            item = convert(path, draft=draft)
            converted.append(item)
            reports.extend(item.reports)
        reports.extend(
            f"left non-task file: {path}"
            for path in sorted(directory.iterdir())
            if path.suffix != ".md"
        )
    numbered = renumber(converted, prefix)
    reports.extend(report for item in numbered for report in item.reports if report not in reports)
    for item in numbered:
        parsed = re.fullmatch(r"TASK-(\d+)(?:\.\d+)?", item.old_id)
        archived = (
            parsed is not None and (source / "completed" / f"task-{item.old_id[5:]}.md").exists()
        )
        target = destination / ("archive" if archived and archive == "move" else "")
        target.mkdir(parents=True, exist_ok=True)
        task_id = ids.TaskId.parse(item.new_id)
        (target / ids.filename(task_id, ids.slugify(item.task.frontmatter.title))).write_text(
            item.task.render()
        )
    for name in ("decisions", "docs", "milestones"):
        if (source / name).exists():
            reports.append(f"left non-task directory: {source / name}")
    return reports


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
