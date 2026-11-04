"""Prepare a Chitty ticket worktree and run Pi in it."""

import os
import shlex
import shutil
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from chitty import git
from chitty.errors import ChittyError
from chitty.inbox import pull as pull_suggestions
from chitty.store import Edit, NextAction, Repo, next_action


class RunInterrupted(Exception):
    """The user interrupted a `chitty run` phase; the command must stop a shell loop."""

    def __init__(self, phase: str) -> None:
        self.phase = phase


@dataclass(frozen=True)
class RunResult:
    action: NextAction
    old_status: str
    new_status: str


def run(repo: Repo, arguments: tuple[str, ...] = ()) -> RunResult:
    """Prepare the selected ticket and run Pi with inherited streams."""
    main_root = _main_checkout(repo.root)
    main_repo = Repo.open(main_root)
    _preflight(main_repo)
    main_repo.refresh_setup()
    if main_repo.config.project:
        try:
            pull_suggestions(main_repo)
        except KeyboardInterrupt:
            raise RunInterrupted("inbox pull") from None

    action = next_action(main_repo)
    stored = main_repo.find(action.id)
    if git.dirty_paths(main_root, stored.path.relative_to(main_root)):
        raise ChittyError(f"{stored.path} has uncommitted changes in the main checkout")
    worktree = _worktree(main_root, action)
    setup = main_repo.config.setup
    assert setup is not None  # `_preflight` rejects an unset setup command.
    _setup(setup, worktree)

    # Each invocation owns a fresh actor identity, including its initial claim.
    os.environ.pop("CHITTY_ACTOR", None)
    os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    os.environ["CHITTY_PI_SESSION_ID"] = str(uuid4())
    work_repo = Repo.open(worktree)
    if action.mode == "work" and work_repo.find(action.id).task.frontmatter.status == "todo":
        work_repo.edit(action.id, Edit(status="doing"))
    old_status = work_repo.find(action.id).task.frontmatter.status
    try:
        completed = subprocess.run(
            ["pi", f"--chitty-{action.mode}", str(action.id), *arguments],
            cwd=worktree,
            check=False,
        )
    except KeyboardInterrupt:
        raise RunInterrupted("Pi") from None
    if completed.returncode == -signal.SIGINT:
        raise RunInterrupted("Pi")
    if completed.returncode:
        raise ChittyError(f"pi exited with status {completed.returncode}")
    # Pi commonly commits from this worktree. Reopen so history is re-read.
    new_status = Repo.open(worktree).find(action.id).task.frontmatter.status
    if new_status == old_status:
        raise ChittyError(
            f"{action.id} was unchanged; only committed changes are visible to `chitty run`"
        )
    return RunResult(action, old_status, new_status)


def _main_checkout(root: Path) -> Path:
    """Find the primary checkout by comparing each worktree's Git directory."""
    common_dir = _git_path(root, "--git-common-dir")
    output = _git(root, "worktree", "list", "--porcelain")
    worktrees = [
        Path(line.removeprefix("worktree "))
        for line in output.splitlines()
        if line.startswith("worktree ")
    ]
    for worktree in worktrees:
        if _git_path(worktree, "--git-dir") == common_dir:
            return worktree.resolve()
    raise ChittyError(f"cannot find the main checkout for {root}")


def _preflight(repo: Repo) -> None:
    if not repo.config.autocommit:
        raise ChittyError("`chitty run` requires autocommit = true")
    if repo.config.setup is None:
        raise ChittyError("`chitty run` requires setup to be configured")
    if shutil.which("pi") is None:
        raise ChittyError("pi is not on PATH")
    if git.current_branch(repo.root) != "main":
        raise ChittyError("the main checkout must be on branch main")


def _worktree(main_root: Path, action: NextAction) -> Path:
    branch = str(action.id).lower()
    existing = git.worktree_for_branch(main_root, branch)
    if existing is not None:
        if existing.resolve() == main_root.resolve():
            raise ChittyError(f"branch {branch} is checked out in the main checkout")
        return existing.resolve()
    destination = main_root / ".worktrees" / branch
    if git.has_local_branch(main_root, branch):
        _git(main_root, "worktree", "add", str(destination), branch)
    elif action.mode == "review":
        raise ChittyError(f"review ticket {action.id} has no branch {branch}")
    else:
        _git(main_root, "worktree", "add", "-b", branch, str(destination), "main")
    return destination


def _setup(command: str, worktree: Path) -> None:
    try:
        completed = subprocess.run(
            shlex.split(command), cwd=worktree, stdin=subprocess.DEVNULL, check=False
        )
    except FileNotFoundError:
        raise ChittyError(f"setup command not found: {command}") from None
    except KeyboardInterrupt:
        raise RunInterrupted("setup") from None
    if completed.returncode:
        raise ChittyError(f"setup exited with status {completed.returncode}")


def _git_path(root: Path, argument: str) -> Path:
    value = _git(root, "rev-parse", argument).strip()
    path = Path(value)
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise ChittyError(completed.stderr.strip() or f"git {' '.join(arguments)} failed")
    return completed.stdout
