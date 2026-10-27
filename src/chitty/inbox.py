"""Machine-local suggestion inboxes."""

from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import yaml

from chitty.config import inbox_path, load_repo_config, register_project, registered_projects
from chitty.errors import ChittyError


def suggest(
    project: str,
    title: str,
    description: str | None,
    create: bool,
    cwd: Path,
    task: str | None = None,
) -> Path:
    """Atomically write a suggestion to a registered project's inbox."""
    target = Path(project).expanduser()
    if target.is_dir():
        config = load_repo_config(target)
        if not config.project:
            raise ChittyError(f"{target} has no project name")
        project = config.project
        register_project(project, target)
    elif project not in registered_projects():
        if not create:
            known = ", ".join(registered_projects()) or "none"
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


def waiting(project: str) -> list[Path]:
    return sorted(inbox_path(project).glob("suggestion-*.md"))


def claim(project: str) -> list[tuple[Path, dict[str, object]]]:
    """Atomically hide waiting suggestions from other pullers before reading."""
    claimed: list[tuple[Path, dict[str, object]]] = []
    for path in waiting(project):
        processing = path.with_suffix(".processing")
        try:
            path.replace(processing)
        except FileNotFoundError:
            continue
        _, frontmatter, body = processing.read_text().split("---\n", 2)
        data = yaml.safe_load(frontmatter)
        if not isinstance(data, dict):
            raise ChittyError(f"{processing}: invalid suggestion frontmatter")
        suggestion = cast(dict[str, object], cast(dict[str, Any], data))
        suggestion["description"] = body.split("## Description\n\n", 1)[-1].strip()
        claimed.append((processing, suggestion))
    return claimed


def _origin(cwd: Path) -> str:
    try:
        return str(load_repo_config(cwd).project or cwd)
    except ChittyError:
        return str(cwd)
