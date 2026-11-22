"""Deterministic Git layouts for ticket source integration tests."""

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tests.support import CONFIG

PLACEMENTS = tuple("abcdefghijklm")


@dataclass(frozen=True)
class Expected:
    title: str | None
    archived: bool = False
    errors: tuple[str, ...] = ()


def git(root: Path, *args: str, date: str = "2026-01-01T00:00:00Z") -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date},
    ).stdout.strip()


def make_repo(parent: Path) -> Path:
    root = Path(tempfile.mkdtemp(dir=parent))
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.com")
    (root / "chitty.toml").write_text(CONFIG)
    return root


def write_ticket(root: Path, number: int, title: str) -> None:
    path = root / f"chitty/tasks/TASK-{number}--example.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\nstatus: todo\ncreated: 2026-01-01\n---\n"
        "\n## Description\n\nFixture.\n"
    )


def edit_uncommitted(root: Path, number: int) -> None:
    write_ticket(root, number, "uncommitted")


def commit(root: Path, day: int) -> None:
    git(root, "add", "--all")
    git(root, "commit", "--allow-empty", "-m", "fixture", date=f"2026-01-{day:02}T00:00:00Z")


def place(root: Path, placement: str, number: int) -> Expected:
    if placement not in PLACEMENTS:
        raise ValueError(placement)
    if placement not in ("f", "i"):
        write_ticket(root, number, "main")
    commit(root, 1)
    if placement == "i":
        write_ticket(root, number, "uncommitted")
        return Expected("uncommitted")
    if placement == "a":
        return Expected("main")
    name = f"task-{number}"
    git(root, "checkout", "-b", "other" if placement == "f" else name)
    if placement != "h":
        write_ticket(root, number, "branch")
    path = f"chitty/tasks/TASK-{number}--example.md"
    if placement == "g":
        (root / "chitty/tasks/archive").mkdir(parents=True, exist_ok=True)
        git(root, "add", path)
        git(root, "mv", path, "chitty/tasks/archive/")
    if placement == "h":
        git(root, "rm", path)
    commit(root, 2)
    if placement in ("c", "d", "e", "l", "m"):
        if placement in ("e", "m"):
            git(root, "checkout", "main")
            git(root, "checkout", "-b", "remote-fixture")
        write_ticket(root, number, "remote")
        commit(root, 3)
        git(root, "update-ref", f"refs/remotes/origin/{name}", "HEAD")
        if placement == "l":
            git(root, "reset", "--hard", "HEAD^")
    git(root, "checkout", "main")
    if placement == "c":
        git(root, "branch", "-D", name)
    if placement in ("e", "m"):
        git(root, "branch", "-D", "remote-fixture")
    if placement == "m":
        git(root, "branch", "-D", name)
    if placement in ("j", "l"):
        git(root, "merge", "--ff-only", name)
    if placement in ("j", "k", "m"):
        write_ticket(root, number, "main-2")
        commit(root, 4)
    if placement in ("k", "m"):
        ref = name if placement == "k" else f"origin/{name}"
        return Expected(None, errors=(f"`TASK-{number}`", f"`{ref}`", "`main`"))
    if placement == "j":
        return Expected("main-2")
    if placement == "g":
        return Expected("branch", archived=True)
    if placement == "h":
        return Expected(None)
    if placement == "f":
        return Expected(None)
    if placement == "e":
        return Expected(None, errors=(name, f"origin/{name}"))
    return Expected("remote" if placement in ("c", "d", "l") else "branch")


def checkout(root: Path, kind: int, number: int) -> Path:
    if kind == 3:
        name = f"task-{number + 1}"
        git(root, "checkout", "-b", name, "main")
        write_ticket(root, number + 1, "other")
        git(root, "add", f"chitty/tasks/TASK-{number + 1}--example.md")
        git(root, "commit", "-m", "other ticket")
        git(root, "checkout", "main")
        path = root / ".worktrees" / name
        git(root, "worktree", "add", str(path), name)
    elif kind == 4:
        path = root / ".worktrees/feature"
        git(root, "worktree", "add", "-b", "feature", str(path), "main")
    elif kind == 5:
        path = root / ".worktrees/detached"
        git(root, "worktree", "add", "--detach", str(path), "main")
    else:
        raise ValueError(kind)
    return path
