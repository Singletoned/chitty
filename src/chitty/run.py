"""Prepare a Chitty ticket worktree and run its configured agent."""

import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast
from uuid import uuid4

from chitty import git
from chitty.actor import actor, run_actor
from chitty.config import CHITTY_VERSION, usage_path, version_key
from chitty.errors import ChittyError
from chitty.inbox import pull as pull_suggestions
from chitty.store import Edit, NextAction, Repo, guide, next_action, ticket_action


class RunInterrupted(Exception):
    """The user interrupted a `chitty run` phase; the command must stop a shell loop."""

    def __init__(self, phase: str) -> None:
        self.phase = phase


@dataclass(frozen=True)
class RunResult:
    action: NextAction
    old_status: str
    new_status: str


def run(
    repo: Repo,
    ticket: str | None,
    arguments: tuple[str, ...] = (),
    agent: str | None = None,
    mode: Literal["work", "review"] | None = None,
) -> RunResult:
    """Prepare the selected ticket and run Pi with inherited streams."""
    if mode is not None and ticket is not None:
        # A named ticket already decides its mode, so a mode could only disagree.
        raise ChittyError("--mode cannot be used with --ticket")
    main_root = _main_checkout(repo.root)
    main_repo = Repo.open(main_root)
    _refuse_stale_linked_worktree(repo, main_repo)
    _preflight(main_repo)
    # Refresh may add a project to legacy setup; only an explicit project opts into inbox pulls.
    project_before_refresh = main_repo.config.project
    main_repo.refresh_setup()
    project = main_repo.config.project
    if project is None:
        raise ChittyError("`chitty run` requires a project name after setup refresh")
    if project_before_refresh:
        try:
            pull_suggestions(main_repo)
        except KeyboardInterrupt:
            raise RunInterrupted("inbox pull") from None

    action = (
        ticket_action(main_repo, main_repo.resolve(ticket))
        if ticket is not None
        else next_action(main_repo, mode=mode)
    )
    agent_command = _agent_command(main_repo, action, agent)
    stored = main_repo.find(action.id)
    if git.dirty_paths(main_root, stored.path.relative_to(main_root)):
        raise ChittyError(f"{stored.path} has uncommitted changes in the main checkout")
    worktree = _worktree(main_root, action)
    setup = main_repo.config.setup
    assert setup is not None  # `_preflight` rejects an unset setup command.
    _setup(setup, worktree)

    # Each invocation owns a fresh actor identity, including its initial claim.
    # A run owns one identity across its claim, agent, and any child process.
    os.environ.pop("CHITTY_ACTOR", None)
    os.environ["CHITTY_ACTOR"] = run_actor(str(uuid4()))
    work_repo = Repo.open(worktree)
    if action.mode == "work" and work_repo.find(action.id).task.frontmatter.status == "todo":
        work_repo.edit(action.id, Edit(status="doing"))
    old_status = work_repo.find(action.id).task.frontmatter.status
    started = datetime.now(UTC)
    elapsed_start = time.monotonic()
    new_status: str | None = None
    models: list[dict[str, Any]] | None = None
    usage_file: Path | None = None
    usage_read = False
    try:
        with tempfile.TemporaryDirectory(prefix="chitty-usage-") as temporary:
            usage_file = Path(temporary) / "session.json"
            previous_usage_file = os.environ.get("CHITTY_USAGE_FILE")
            os.environ["CHITTY_USAGE_FILE"] = str(usage_file)
            try:
                try:
                    completed = subprocess.run(
                        [*agent_command, *arguments], cwd=worktree, check=False
                    )
                except FileNotFoundError:
                    raise ChittyError(f"agent command not found: {agent_command[0]}") from None
                except KeyboardInterrupt:
                    raise RunInterrupted("agent") from None
                finally:
                    if previous_usage_file is None:
                        os.environ.pop("CHITTY_USAGE_FILE", None)
                    else:
                        os.environ["CHITTY_USAGE_FILE"] = previous_usage_file
                if completed.returncode == -signal.SIGINT:
                    raise RunInterrupted("agent")
                if completed.returncode:
                    raise ChittyError(f"agent exited with status {completed.returncode}")
                models = _read_usage(usage_file)
                usage_read = True

                # Pi commonly commits from this worktree. Reopen so history is re-read.
                new_status = _status_after_agent(main_root, worktree, action)
                if new_status == old_status:
                    raise ChittyError(
                        f"{action.id} was unchanged; only committed changes are visible "
                        "to `chitty run`"
                    )
            finally:
                if not usage_read:
                    models = _read_usage(usage_file)
                    usage_read = True
    finally:
        if new_status is None:
            try:
                new_status = _status_after_agent(main_root, worktree, action)
            except Exception:  # noqa: BLE001 - logging must not mask the agent error
                new_status = None
        _record_usage(
            project,
            {
                "ticket": str(action.id),
                "mode": action.mode,
                "actor": actor(),
                "started": started.isoformat().replace("+00:00", "Z"),
                "seconds": round(time.monotonic() - elapsed_start, 3),
                "status_before": old_status,
                "status_after": new_status,
                "models": models,
            },
        )
    assert new_status is not None
    return RunResult(action, old_status, new_status)


def _read_usage(path: Path) -> list[dict[str, Any]] | None:
    try:
        if not path.exists():
            raise ValueError("file is missing")
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise TypeError("expected a JSON object with a `sessions` object")
        data_dict = cast(dict[str, object], data)
        if not isinstance(data_dict.get("sessions"), dict):
            raise TypeError("expected a JSON object with a `sessions` object")
        sessions = cast(dict[str, object], data_dict["sessions"])
        totals: dict[tuple[str, str], dict[str, Any]] = {}
        for entries in sessions.values():
            if not isinstance(entries, list):
                raise TypeError("each session must contain a list of entries")
            for raw_entry in cast(list[object], entries):
                if not isinstance(raw_entry, dict):
                    raise TypeError("each usage entry must be an object")
                entry = cast(dict[str, Any], raw_entry)
                fields = ("provider", "model", "input", "output", "cacheRead", "cacheWrite", "cost")
                if any(field not in entry for field in fields):
                    raise ValueError("usage entry is missing a field")
                if not isinstance(entry["provider"], str) or not isinstance(entry["model"], str):
                    raise TypeError("provider and model must be strings")
                if any(
                    not isinstance(entry[field], (int, float)) or isinstance(entry[field], bool)
                    for field in fields[2:-1]
                ):
                    raise ValueError("token counts must be numbers")
                if entry["cost"] is not None and (
                    not isinstance(entry["cost"], (int, float)) or isinstance(entry["cost"], bool)
                ):
                    raise ValueError("cost must be a number or null")
                key = (entry["provider"], entry["model"])
                total = totals.setdefault(
                    key,
                    {
                        "provider": entry["provider"],
                        "model": entry["model"],
                        "input": 0,
                        "output": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                        "cost": 0,
                    },
                )
                for field in fields[2:-1]:
                    total[field] += entry[field]
                if total["cost"] is None or entry["cost"] is None:
                    total["cost"] = None
                else:
                    total["cost"] += entry["cost"]
        return list(totals.values())
    except Exception as error:  # noqa: BLE001 - invalid usage must not abort the run
        print(f"warning: cannot read usage file {path}: {error}", file=sys.stderr)
        return None


def _record_usage(project: str, record: dict[str, Any]) -> None:
    try:
        _append_usage(project, record)
    except Exception as error:  # noqa: BLE001 - logging must not change the exit code
        print(f"warning: cannot write usage log: {error}", file=sys.stderr)


def _append_usage(project: str, record: dict[str, Any]) -> None:
    path = usage_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(record, separators=(",", ":")) + "\n")


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


def _refuse_stale_linked_worktree(repo: Repo, main_repo: Repo) -> None:
    if not git.is_linked_worktree(repo.root):
        return
    recorded = main_repo.config.chitty_version
    if recorded is not None and version_key(recorded) >= version_key(CHITTY_VERSION):
        return
    recorded_name = recorded if recorded is not None else "unrecorded"
    raise ChittyError(
        f"linked worktree uses Chitty {CHITTY_VERSION}, but the main checkout setup "
        f"records {recorded_name}; run `chitty run` from the main checkout"
    )


def _preflight(repo: Repo) -> None:
    if not repo.config.autocommit:
        raise ChittyError("`chitty run` requires autocommit = true")
    if repo.config.setup is None:
        raise ChittyError("`chitty run` requires setup to be configured")
    if git.current_branch(repo.root) != "main":
        raise ChittyError("the main checkout must be on branch main")


def _agent_command(repo: Repo, action: NextAction, agent: str | None = None) -> tuple[str, ...]:
    """Parse and validate the selected command after setup refreshes it."""
    if agent is None:
        setting = "agent_command"
        command = repo.config.agent_command
    else:
        available = sorted(repo.config.agent_commands)
        if agent not in repo.config.agent_commands:
            names = ", ".join(available) if available else "none"
            raise ChittyError(f"unknown agent {agent!r}; available names: {names}")
        setting = f"agent_commands.{agent}"
        command = repo.config.agent_commands[agent]
    example = (
        'agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts '
        '--chitty-{mode} {id}"'
    )
    if command is None or not command.strip():
        if setting == "agent_command":
            raise ChittyError(f"`chitty run` requires agent_command; for example: {example}")
        raise ChittyError(f"`chitty run` requires {setting}")
    try:
        words = shlex.split(command)
    except ValueError as error:
        raise ChittyError(f"invalid {setting}: {error}") from None
    if ("{mode}" not in command or "{id}" not in command) and "{prompt}" not in command:
        raise ChittyError(f"{setting} must contain both {{mode}} and {{id}}, or {{prompt}}")
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
        raise ChittyError(f"{setting} must use an absolute path when its first word contains '/'")
    executable = shutil.which(first)
    if executable is None:
        raise ChittyError(f"{setting} executable is not on PATH: {first}")
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
