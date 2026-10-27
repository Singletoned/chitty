"""Pure conversion of one legacy Backlog.md task file."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml

from chitty import ids
from chitty.model import DESCRIPTION, NOTES, PLAN, SECTION_ORDER, SUMMARY, Task, new_task
from chitty.store import Change, Context, Repo, StoredTask, guide

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
    dependencies: tuple[str, ...] = ()


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
    raw_dependencies = cast(list[Any], fields.get("dependencies") or [])
    dependencies = tuple(str(value) for value in raw_dependencies)
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
            "depends_on": [value for value in dependencies if re.fullmatch(r"TASK-\d+", value)],
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
    return ConvertedTask(old_id, task, tuple(reports), dependencies)


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
    legacy_dependencies = item.dependencies or tuple(task.frontmatter.depends_on)
    dependencies = [_rewrite(value, mapping, reports, item.old_id) for value in legacy_dependencies]
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


def import_directory(
    source: Path, repo: Repo, destination: Context, agents: Path | None = None
) -> list[str]:
    """Convert a legacy backlog after all source files validate successfully."""
    prefix = destination.prefix
    locations = (
        ("tasks", False, False),
        ("drafts", True, False),
        ("completed", False, True),
        ("archive", False, True),
    )
    converted: list[ConvertedTask] = []
    archived_ids: set[str] = set()
    reports: list[str] = []
    for name, draft, archived in locations:
        directory = source / name
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            item = convert(path, draft=draft)
            converted.append(item)
            if archived:
                archived_ids.add(item.old_id)
            reports.extend(item.reports)
        reports.extend(
            f"left non-task file: {path}"
            for path in sorted(directory.iterdir())
            if path.suffix != ".md"
        )
    numbered = renumber(converted, prefix)
    reports.extend(report for item in numbered for report in item.reports if report not in reports)
    unresolved = [report for report in reports if "reference to unknown ID" in report]
    if unresolved:
        raise ValueError("cannot import with unresolved references: " + "; ".join(unresolved))
    deleted_ids = {
        item.new_id
        for item in numbered
        if item.old_id in archived_ids and repo.config.archive == "delete"
    }
    retained = [
        item
        for item in numbered
        if not (item.old_id in archived_ids and repo.config.archive == "delete")
    ]
    retained = [_without_deleted_references(item, deleted_ids) for item in retained]
    _validate_relationships(retained)
    stored: list[StoredTask] = []
    for item in retained:
        archived = item.old_id in archived_ids
        task = item.task
        if archived:
            task = task.with_history(date.today(), task.frontmatter.status, "archived")
        task_id = ids.TaskId.parse(item.new_id)
        directory = destination.archive_directory if archived else destination.directory
        path = directory / ids.filename(task_id, ids.slugify(task.frontmatter.title))
        directory.mkdir(parents=True, exist_ok=True)
        path.write_text(task.render())
        stored.append(StoredTask(task_id, destination.name, path, archived, task))
    agent_path = agents if stored and agents and agents.exists() else None
    previous_agents: str | None = None
    if agent_path:
        previous_agents = agent_path.read_text()
        pattern = r"(?ms)^## Backlog\.md Workflow\n.*?(?=^## |\Z)"
        updated, count = re.subn(pattern, guide().rstrip() + "\n", previous_agents)
        if count:
            agent_path.write_text(updated)
        else:
            previous_agents = None
    if stored:
        paths = [task.path for task in stored]
        if agent_path and previous_agents is not None:
            paths.append(agent_path)
        try:
            repo.finalize(Change(stored[-1], tuple(paths), tuple(stored)), "import")
        except Exception:
            for task in stored:
                task.path.unlink(missing_ok=True)
            if agent_path and previous_agents is not None:
                agent_path.write_text(previous_agents)
            raise
    for name in ("decisions", "docs", "milestones"):
        if (source / name).exists():
            reports.append(f"left non-task directory: {source / name}")
    return reports


def _without_deleted_references(item: RenumberedTask, deleted_ids: set[str]) -> RenumberedTask:
    """Apply delete-mode relationship semantics to an imported task."""
    task = item.task
    dependencies = [
        reference for reference in task.frontmatter.depends_on if reference not in deleted_ids
    ]
    if dependencies != task.frontmatter.depends_on:
        task = task.with_field("depends_on", dependencies)
    if task.frontmatter.parent in deleted_ids:
        task = task.with_field("parent", None)
    return replace(item, task=task)


def _validate_relationships(tasks: list[RenumberedTask]) -> None:
    """Reject generated dependency and parent relationships before writing files."""
    by_id: dict[ids.TaskId, list[RenumberedTask]] = {}
    for item in tasks:
        by_id.setdefault(ids.TaskId.parse(item.new_id), []).append(item)
    dependencies: dict[ids.TaskId, set[ids.TaskId]] = {task_id: set() for task_id in by_id}
    parents: dict[ids.TaskId, set[ids.TaskId]] = {task_id: set() for task_id in by_id}
    problems = [
        f"{task_id} is used by more than one imported task"
        for task_id, items in by_id.items()
        if len(items) > 1
    ]
    for task_id, items in by_id.items():
        if len(items) > 1:
            continue
        item = items[0]
        for reference in item.task.frontmatter.depends_on:
            dependency = ids.TaskId.parse(reference)
            if dependency == task_id:
                problems.append(f"{task_id}: depends_on lists the task itself")
            elif dependency not in by_id:
                problems.append(f"{task_id}: depends_on {reference}: no such task")
            else:
                dependencies[task_id].add(dependency)
        reference = item.task.frontmatter.parent
        if reference is None:
            continue
        parent = ids.TaskId.parse(reference)
        if parent == task_id:
            problems.append(f"{task_id}: parent lists the task itself")
        elif parent not in by_id:
            problems.append(f"{task_id}: parent {reference}: no such task")
        else:
            parents[task_id].add(parent)
    for field, graph in (("depends_on", dependencies), ("parent", parents)):
        for cycle in _cycles(graph):
            problems.append(f"{field} cycle: {', '.join(map(str, cycle))}")
    if problems:
        raise ValueError("cannot import invalid task relationships: " + "; ".join(problems))


def _cycles(graph: dict[ids.TaskId, set[ids.TaskId]]) -> list[tuple[ids.TaskId, ...]]:
    """Return each cyclic strongly connected component in stable order."""
    index = 0
    indices: dict[ids.TaskId, int] = {}
    lowlinks: dict[ids.TaskId, int] = {}
    stack: list[ids.TaskId] = []
    on_stack: set[ids.TaskId] = set()
    cycles: list[tuple[ids.TaskId, ...]] = []

    def visit(task_id: ids.TaskId) -> None:
        nonlocal index
        indices[task_id] = index
        lowlinks[task_id] = index
        index += 1
        stack.append(task_id)
        on_stack.add(task_id)
        for dependency in sorted(graph[task_id], key=str):
            if dependency not in indices:
                visit(dependency)
                lowlinks[task_id] = min(lowlinks[task_id], lowlinks[dependency])
            elif dependency in on_stack:
                lowlinks[task_id] = min(lowlinks[task_id], indices[dependency])
        if lowlinks[task_id] != indices[task_id]:
            return
        component: list[ids.TaskId] = []
        while True:
            dependency = stack.pop()
            on_stack.remove(dependency)
            component.append(dependency)
            if dependency == task_id:
                break
        if len(component) > 1:
            cycles.append(tuple(sorted(component, key=str)))

    for task_id in sorted(graph, key=str):
        if task_id not in indices:
            visit(task_id)
    return sorted(cycles, key=lambda cycle: tuple(map(str, cycle)))


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
