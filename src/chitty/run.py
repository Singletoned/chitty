"""Prepare a Chitty ticket worktree and run its configured agent."""

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
from chitty.store import Edit, NextAction, Repo, guide, next_action


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
    # Refresh may add a project to legacy setup; only an explicit project opts into inbox pulls.
    project = main_repo.config.project
    main_repo.refresh_setup()
    if project:
        try:
            pull_suggestions(main_repo)
        except KeyboardInterrupt:
            raise RunInterrupted("inbox pull") from None

    action = next_action(main_repo)
    agent_command = _agent_command(main_repo, action)
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
        completed = subprocess.run([*agent_command, *arguments], cwd=worktree, check=False)
    except FileNotFoundError:
        raise ChittyError(f"agent command not found: {agent_command[0]}") from None
    except KeyboardInterrupt:
        raise RunInterrupted("agent") from None
    if completed.returncode == -signal.SIGINT:
        raise RunInterrupted("agent")
    if completed.returncode:
        raise ChittyError(f"agent exited with status {completed.returncode}")
    # Pi commonly commits from this worktree. Reopen so history is re-read.
    new_status = _status_after_agent(main_root, worktree, action)
    if new_status == old_status:
        raise ChittyError(
            f"{action.id} was unchanged; only committed changes are visible to `chitty run`"
        )
    return RunResult(action, old_status, new_status)


def _status_after_agent(main_root: Path, worktree: Path, action: NextAction) -> str:
    if worktree.exists():
        return Repo.open(worktree).find(action.id).task.frontmatter.status

    # A passed review may merge and remove its worktree before `run` reports the result.
    main_repo = Repo.open(main_root)
    new_status = main_repo.find(action.id).task.frontmatter.status
    branch = str(action.id).lower()
    if git.has_local_branch(main_root, branch):
        return new_status
    if new_status != "done":
        raise ChittyError(f"{action.id} was lost after its worktree and branch were removed")
    return new_status


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
    if git.current_branch(repo.root) != "main":
        raise ChittyError("the main checkout must be on branch main")


def _agent_command(repo: Repo, action: NextAction) -> tuple[str, ...]:
    """Parse and validate the configured command after setup refreshes it."""
    command = repo.config.agent_command
    example = (
        'agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts '
        '--chitty-{mode} {id}"'
    )
    if command is None or not command.strip():
        raise ChittyError(f"`chitty run` requires agent_command; for example: {example}")
    try:
        words = shlex.split(command)
    except ValueError as error:
        raise ChittyError(f"invalid agent_command: {error}") from None
    if ("{mode}" not in command or "{id}" not in command) and "{prompt}" not in command:
        raise ChittyError("agent_command must contain both {mode} and {id}, or {prompt}")
    prompt = guide(action.mode, str(action.id)) if "{prompt}" in command else ""
    rendered = tuple(
        os.path.expanduser(word)
        .replace("{mode}", action.mode)
        .replace("{id}", str(action.id))
        .replace("{prompt}", prompt)
        for word in words
    )
    first = rendered[0]
    if "/" in first and not Path(first).is_absolute():
        raise ChittyError(
            "agent_command must use an absolute path when its first word contains '/'"
        )
    executable = shutil.which(first)
    if executable is None:
        raise ChittyError(f"agent_command executable is not on PATH: {first}")
    # Resolve now: a relative PATH entry can point elsewhere after changing to the worktree.
    resolved = Path(executable)
    if not resolved.is_absolute():
        resolved = repo.root / resolved
    return (str(resolved.resolve()), *rendered[1:])


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
