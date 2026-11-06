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
import tomllib
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast
from uuid import uuid4

from chitty import git, locks
from chitty.actor import actor, run_actor
from chitty.config import (
    CHITTY_VERSION,
    CONFIG_NAME,
    PYPROJECT_NAME,
    config_source,
    usage_path,
    version_key,
)
from chitty.errors import ChittyError, ManagedGuideError
from chitty.store import (
    AGENTS_FILE,
    Edit,
    NextAction,
    Repo,
    guide,
    managed_block,
    next_action,
    ticket_action,
)

# Each lost race removes a candidate, so a few attempts are plenty.
RUN_LOCK_ATTEMPTS = 10


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
    owner: str | None = None,
) -> RunResult:
    """Prepare the selected ticket and run Pi with inherited streams."""
    if mode is not None and ticket is not None:
        # A named ticket already decides its mode, so a mode could only disagree.
        raise ChittyError("--mode cannot be used with --ticket")
    if ticket is not None and owner is not None:
        raise ChittyError("--owner cannot be used with --ticket")
    if owner in ("", "human"):
        raise ChittyError("--owner must name an agent, not human or empty")
    # Set the run identity before selecting or locking a ticket so the lock
    # record describes the session even when setup or preparation fails.
    os.environ.pop("CHITTY_ACTOR", None)
    os.environ["CHITTY_ACTOR"] = run_actor(str(uuid4()))
    main_root = git.main_checkout(repo.root)
    main_repo = Repo.open(main_root)
    _refuse_stale_linked_worktree(repo, main_repo)
    _preflight(main_repo)
    main_repo.refresh_setup()
    project = main_repo.config.project
    if project is None:
        raise ChittyError("`chitty run` requires a project name after setup refresh")

    with ExitStack() as held:
        action = _lock_ticket(held, main_repo, ticket, mode, owner)
        return _run_ticket(main_repo, project, action, arguments, agent)


def _lock_ticket(
    held: ExitStack,
    main_repo: Repo,
    ticket: str | None,
    mode: Literal["work", "review"] | None,
    owner: str | None,
) -> NextAction:
    """Choose the ticket and take its run lock, which `held` releases."""
    if ticket is not None:
        action = ticket_action(main_repo, main_repo.resolve(ticket))
        held.enter_context(
            locks.run_lock(main_repo.root, str(action.id), actor=actor(), mode=action.mode)
        )
        return action
    for _ in range(RUN_LOCK_ATTEMPTS - 1):
        action = next_action(main_repo, mode=mode, owner=owner)
        try:
            held.enter_context(
                locks.run_lock(main_repo.root, str(action.id), actor=actor(), mode=action.mode)
            )
        except locks.TicketLocked:
            # Another run locked it after `next_action` looked; it skips it now.
            continue
        return action
    action = next_action(main_repo, mode=mode, owner=owner)
    held.enter_context(
        locks.run_lock(main_repo.root, str(action.id), actor=actor(), mode=action.mode)
    )
    return action


def _run_ticket(
    main_repo: Repo,
    project: str,
    action: NextAction,
    arguments: tuple[str, ...],
    agent: str | None,
) -> RunResult:
    """Prepare the locked ticket's worktree and run its agent."""
    main_root = main_repo.root
    agent_command = _agent_command(main_repo, action, agent)
    stored = main_repo.find(action.id)
    if git.dirty_paths(main_root, stored.path.relative_to(main_root)):
        raise ChittyError(f"{stored.path} has uncommitted changes in the main checkout")
    worktree = _worktree(main_root, action, main_repo.config.main_branch)
    setup = main_repo.config.setup
    check = main_repo.config.check
    assert setup is not None  # `_preflight` rejects an unset setup command.
    assert check is not None  # `_preflight` rejects an unset check command.
    if action.mode == "work":
        _setup(setup, worktree)

    if action.mode == "review":
        # The config may be deleted on a branch, so use main's config until the
        # review preflight has confirmed that the branch still has one.
        work_repo = Repo(worktree, main_repo.config)
        # The run's own actor never worked on the ticket, so it may fail it.
        failed = _prepare_review(work_repo, worktree, action, main_repo.config.main_branch)
        if failed is not None:
            return failed
        work_repo = Repo.open(worktree)
        # After the rebase, because the rebase can change dependencies.
        _setup(setup, worktree)
    else:
        work_repo = Repo.open(worktree)
    if failed := _run_check(work_repo, worktree, action, check):
        return failed
    if action.mode == "work" and work_repo.find(action.id).task.frontmatter.status == "todo":
        work_repo.edit(action.id, claim_edit())
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
                runner_chitty = Path(sys.executable).parent / "chitty"
                if not runner_chitty.is_file():
                    raise ChittyError(f"runner chitty executable not found: {runner_chitty}")
                agent_environment = os.environ.copy()
                agent_environment["PATH"] = os.pathsep.join(
                    (str(runner_chitty.parent), agent_environment.get("PATH", ""))
                )
                agent_environment.pop("VIRTUAL_ENV", None)
                agent_environment.pop("UV_PROJECT_ENVIRONMENT", None)
                try:
                    completed = subprocess.run(
                        [*agent_command, *arguments],
                        cwd=worktree,
                        env=agent_environment,
                        check=False,
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
    source = config_source(repo.root)
    assert source is not None  # `Repo.open` rejects repositories without config.
    config_file = source.relative_to(repo.root)
    if not repo.config.autocommit:
        raise ChittyError(
            f"`chitty run` requires `autocommit = true` in {config_file}, "
            "so ticket changes reach every branch; `chitty init --autocommit` sets it"
        )
    if repo.config.setup is None:
        raise ChittyError(
            f"`chitty run` requires `setup` in {config_file}: the command that installs "
            "a new ticket worktree's environment before the agent starts, for example "
            'setup = "make install"'
        )
    if repo.config.check is None:
        raise ChittyError(
            f"`chitty run` requires `check` in {config_file}: the command that validates "
            'a ticket worktree before the agent starts, for example check = "make check"'
        )
    if git.current_branch(repo.root) != repo.config.main_branch:
        raise ChittyError(f"the main checkout must be on branch {repo.config.main_branch}")


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


def _prepare_review(
    work_repo: Repo, worktree: Path, action: NextAction, main_branch: str
) -> RunResult | None:
    """Rebase a review ticket onto the integration branch, or fail it back to its worker.

    The reviewer then sees exactly what would land. Returns the status change
    when the ticket fails here, so no review session is spent on it.
    """
    if uncommitted := git.uncommitted_paths(worktree):
        listed = ", ".join(f"`{path}`" for path in uncommitted)
        return _fail_review(
            work_repo,
            action,
            f"Review failed (work): the worktree has uncommitted changes: {listed}.",
        )
    try:
        conflicts = git.rebase(worktree, main_branch)
    except KeyboardInterrupt:
        if git.rebase_in_progress(worktree):
            git.abort_rebase(worktree)
        raise RunInterrupted("rebase") from None
    if conflicts:
        listed = ", ".join(f"`{path}`" for path in conflicts)
        return _fail_review(
            work_repo,
            action,
            f"Review failed (integration): rebasing onto `{main_branch}` conflicts in {listed}.",
        )
    if changed := _changed_config(worktree, main_branch):
        return _fail_review(
            work_repo,
            action,
            "Review failed (work): the branch changes "
            f"`{changed}`; only `chitty init` on the main checkout may change it.",
        )
    if _changed_agents_block(worktree, main_branch):
        return _fail_review(
            work_repo,
            action,
            "Review failed (work): the branch changes Chitty's managed block in AGENTS.md; "
            "only chitty init on the main checkout may change it. Restore that block from main.",
        )
    return None


def _changed_agents_block(worktree: Path, main_branch: str | None = None) -> bool:
    """Return whether the branch changes or damages the managed guide block."""
    if main_branch is None:
        main_branch = Repo.open(git.main_checkout(worktree)).config.main_branch
    agents = worktree / AGENTS_FILE
    branch_text = agents.read_text() if agents.exists() else None
    main_text = git.file_at(worktree, main_branch, AGENTS_FILE)
    if (branch_text is None) != (main_text is None):
        return True
    try:
        branch_block = managed_block(branch_text) if branch_text is not None else None
    except ManagedGuideError:
        return True
    try:
        main_block = managed_block(main_text) if main_text is not None else None
    except ManagedGuideError:
        main_block = None
    return branch_block != main_block


def _changed_config(worktree: Path, main_branch: str) -> str | None:
    """Return the Chitty config path when the rebased branch changed it."""
    source = config_source(worktree)
    if source is None:
        # A deleted config has no current source to compare, but its path is
        # still present in main and must be reported as a branch change.
        return _main_config_path(worktree, main_branch)
    relative = source.relative_to(worktree)
    if source.name == CONFIG_NAME:
        result = subprocess.run(
            ["git", "diff", "--quiet", f"{main_branch}...HEAD", "--", str(relative)],
            cwd=worktree,
            check=False,
        )
        if result.returncode == 1:
            return str(relative)
        if result.returncode:
            raise ChittyError(f"cannot compare {relative} with `{main_branch}`")
        return None

    current = tomllib.loads(source.read_text()).get("tool", {}).get("chitty")
    try:
        main_text = _git(worktree, "show", f"{main_branch}:{relative}")
    except ChittyError:
        return str(relative)
    main = tomllib.loads(main_text).get("tool", {}).get("chitty")
    return str(relative) if current != main else None


def _main_config_path(worktree: Path, main_branch: str) -> str | None:
    """Return the Chitty config path recorded in the integration tree."""
    try:
        _git(worktree, "show", f"{main_branch}:{CONFIG_NAME}")
    except ChittyError:
        pass
    else:
        return CONFIG_NAME

    try:
        text = _git(worktree, "show", f"{main_branch}:{PYPROJECT_NAME}")
        data = tomllib.loads(text)
    except (ChittyError, tomllib.TOMLDecodeError):
        return None
    tool = data.get("tool")
    return PYPROJECT_NAME if isinstance(tool, dict) and "chitty" in tool else None


def claim_edit() -> Edit:
    """Return the fixed edit used to claim a todo ticket."""
    return Edit(status="doing")


def fail_review_edit(note: str) -> Edit:
    """Return the fixed edit used when a review cannot proceed."""
    return Edit(status="doing", note=note, skip_verdicts=True)


def _fail_review(work_repo: Repo, action: NextAction, note: str) -> RunResult:
    """Move a review ticket to `doing` through `Repo.edit`, so escalation counts it."""
    change = work_repo.edit(action.id, fail_review_edit(note))
    return RunResult(action, "review", change.task.task.frontmatter.status)


def _worktree(main_root: Path, action: NextAction, main_branch: str) -> Path:
    branch = str(action.id).lower()
    destination = main_root / ".worktrees" / branch
    # A rebase stopped part-way detaches HEAD, so Git no longer lists the
    # worktree under its branch. It needs a person, not a second worktree.
    # Its own `.git` file, so a stray directory never reads the main checkout's state.
    if (destination / ".git").exists() and git.rebase_in_progress(destination):
        raise ChittyError(
            f"{destination} has an unfinished rebase; finish it or run `git rebase --abort` there"
        )
    existing = git.worktree_for_branch(main_root, branch)
    if existing is not None:
        if existing.resolve() == main_root.resolve():
            raise ChittyError(f"branch {branch} is checked out in the main checkout")
        if git.rebase_in_progress(existing):
            raise ChittyError(
                f"{existing} has an unfinished rebase; finish it or run `git rebase --abort` there"
            )
        return existing.resolve()
    if git.has_local_branch(main_root, branch):
        _git(main_root, "worktree", "add", str(destination), branch)
    elif action.mode == "review":
        raise ChittyError(f"review ticket {action.id} has no branch {branch}")
    else:
        _git(main_root, "worktree", "add", "-b", branch, str(destination), main_branch)
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


def _run_check(
    work_repo: Repo, worktree: Path, action: NextAction, command: str
) -> RunResult | None:
    """Validate the prepared worktree before spending an agent or review session."""
    print(f"Running check in {worktree}...", file=sys.stderr)
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=worktree,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        output = f"check command not found: {command}"
        return _fail_check(work_repo, action, output)
    except KeyboardInterrupt:
        raise RunInterrupted("check") from None
    if completed.returncode == 0:
        return None
    lines = completed.stdout.splitlines()[-20:]
    output = "\n".join(lines) or "(no output)"
    return _fail_check(
        work_repo,
        action,
        f"check exited with status {completed.returncode}:\n{output}",
    )


def _fail_check(work_repo: Repo, action: NextAction, detail: str) -> RunResult:
    old_status = work_repo.find(action.id).task.frontmatter.status
    change = work_repo.edit(
        action.id,
        Edit(status="doing", note=f"Review failed (work): {detail}", skip_verdicts=True),
    )
    return RunResult(action, old_status, change.task.task.frontmatter.status)


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise ChittyError(completed.stderr.strip() or f"git {' '.join(arguments)} failed")
    return completed.stdout
