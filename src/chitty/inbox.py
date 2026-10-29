"""Machine-local suggestion inboxes."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import yaml

from chitty.config import inbox_path, load_repo_config, register_project, registered_projects
from chitty.errors import ChittyError
from chitty.store import Change, Edit, Repo


def suggest(
    project: str,
    title: str,
    description: str | None,
    create: bool,
    cwd: Path,
    task: str | None = None,
) -> Path:
    """Atomically write a suggestion to a registered project's inbox."""
    projects = registered_projects()
    if project in projects:
        pass
    elif _is_project_path(project):
        target = Path(project).expanduser()
        config = load_repo_config(target)
        if not config.project:
            raise ChittyError(f"{target} has no project name")
        project = config.project
        register_project(project, target)
    else:
        if not create:
            known = ", ".join(projects) or "none"
            raise ChittyError(f"unknown project {project!r}; known projects: {known}; use --create")
        register_project(project, None)
    directory = inbox_path(project)
    origin = _origin(cwd)
    task_line = f"task: {task}\n" if task else ""
    text = f"---\ntitle: {title}\ncreated: {date.today().isoformat()}\norigin: {origin}\n"
    text += task_line + "---\n\n"
    if description:
        text += f"## Description\n\n{description}\n"
    fd, temporary = tempfile.mkstemp(prefix=".suggest-", dir=directory, text=True)
    with os.fdopen(fd, "w") as output:
        output.write(text)
    path = directory / f"suggestion-{uuid4().hex}.md"
    Path(temporary).replace(path)
    return path


def _is_project_path(project: str) -> bool:
    return "/" in project or project == "." or project.startswith(("~", "."))


def _project(repo: Repo) -> str:
    """Return the registered name required for inbox operations."""
    if not repo.config.project:
        raise ChittyError("this repository has no project name")
    return repo.config.project


def pull(repo: Repo) -> list[str]:
    """Turn claimed suggestions into backlog tasks in one repository."""
    project = _project(repo)
    register_project(project, repo.root)
    cleanup_completed(project)
    task_ids: list[str] = []
    changes: list[Change] = []
    created_paths: list[Path] = []
    configured = repo.config
    claimed: list[tuple[Path, dict[str, object]]] = []
    finalized = False
    try:
        claimed = claim(project)
        repo.config = configured.model_copy(update={"autocommit": False})
        for _, item in claimed:
            created = repo.add(
                repo.default_context,
                str(item["title"]),
                str(item["description"]) or None,
                [],
                {"status": "backlog"},
                date.today(),
            )
            created_paths.extend(created.paths)
            origin = item.get("origin", "unknown")
            changes.append(repo.edit(created.task.id, Edit(note=f"Suggestion origin: {origin}")))
            task_ids.append(str(created.task.id))
        if changes:
            paths = tuple(path for change in changes for path in change.paths)
            tasks = tuple(task for change in changes for task in change.tasks)
            repo.config = configured
            repo.finalize(Change(changes[-1].task, paths, tasks), "pull")
        finalized = True
        for path, _ in claimed:
            path.replace(path.with_suffix(".done"))
        cleanup_completed(project)
        return task_ids
    except BaseException:
        if not finalized:
            for path in created_paths:
                path.unlink(missing_ok=True)
            release(path for path, _ in claimed)
        raise
    finally:
        repo.config = configured


def cleanup_completed(project: str) -> None:
    """Remove source suggestions after their imported tasks are finalized."""
    for path in inbox_path(project).glob("suggestion-*.done"):
        path.unlink()


def waiting(project: str) -> list[Path]:
    return sorted(inbox_path(project).glob("suggestion-*.md"))


def list_waiting(repo: Repo) -> list[dict[str, object]]:
    """Read suggestion metadata without claiming or modifying inbox files."""
    return [_read_suggestion(path) for path in waiting(_project(repo))]


def _read_suggestion(path: Path) -> dict[str, object]:
    _, frontmatter, body = path.read_text().split("---\n", 2)
    data = yaml.safe_load(frontmatter)
    if not isinstance(data, dict):
        raise ChittyError(f"{path}: invalid suggestion frontmatter")
    suggestion = cast(dict[str, object], cast(dict[str, Any], data))
    suggestion["created"] = str(suggestion["created"])
    suggestion["description"] = body.split("## Description\n\n", 1)[-1].strip()
    return suggestion


def claim(project: str) -> list[tuple[Path, dict[str, object]]]:
    """Atomically hide waiting suggestions from other pullers before reading."""
    claimed: list[tuple[Path, dict[str, object]]] = []
    processing_paths: list[Path] = []
    try:
        for path in waiting(project):
            processing = path.with_suffix(".processing")
            try:
                path.replace(processing)
            except FileNotFoundError:
                continue
            processing_paths.append(processing)
            claimed.append((processing, _read_suggestion(processing)))
        return claimed
    except BaseException:
        release(processing_paths)
        raise


def release(paths: Iterable[Path]) -> None:
    """Return unprocessed claims to the waiting inbox after a failed pull."""
    for path in paths:
        if path.exists():
            path.replace(path.with_suffix(".md"))


def _origin(cwd: Path) -> str:
    try:
        return str(load_repo_config(cwd).project or cwd)
    except ChittyError:
        return str(cwd)
