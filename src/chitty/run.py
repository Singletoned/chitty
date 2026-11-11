"""Prepare a Chitty ticket worktree and run its configured agent."""

import json
import os
import re
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
from chitty.errors import NO_NEXT_TICKET_EXIT, ChittyError, ManagedGuideError
from chitty.store import (
    AGENTS_FILE,
    Edit,
    NextAction,
    Repo,
    StoredTask,
    guide,
    managed_block,
    next_action,
    ticket_action,
)

# Each lost race removes a candidate, so a few attempts are plenty.
RUN_LOCK_ATTEMPTS = 10
RUN_LOOP_PAUSE_SECONDS = 60
AGENT_KILL_GRACE_SECONDS = 2


def agent_exit(
    returncode: int, timed_out: bool
) -> Literal["interrupted", "timed out", "failed", "ok"]:
    if timed_out:
        return "timed out"
    if returncode == -signal.SIGINT:
        return "interrupted"
    if returncode:
        return "failed"
    return "ok"


def status_outcome(old_status: str, new_status: str) -> Literal["unchanged", "land", "changed"]:
    if old_status == new_status:
        return "unchanged"
    if new_status == "done":
        return "land"
    return "changed"


def loop_step(returncode: int) -> tuple[bool, int]:
    if returncode in (0, NO_NEXT_TICKET_EXIT):
        return True, 0
    return False, returncode if returncode > 0 else 128 - returncode


def _command_environment() -> dict[str, str]:
    """Copy the environment without shell-selected project virtualenvs."""
    environment = os.environ.copy()
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("UV_PROJECT_ENVIRONMENT", None)
    return environment


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
    modes: tuple[Literal["work", "review"], ...] = (),
    owner: str | None = None,
) -> RunResult:
    """Prepare the selected ticket and run Pi with inherited streams."""
    if modes and ticket is not None:
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

    if ticket is None:
        landed = _land_pending(main_repo)
        if landed is not None:
            return landed

    with ExitStack() as held:
        action = _lock_ticket(held, main_repo, ticket, modes, owner)
        return _run_ticket(main_repo, project, action, arguments, agent)


def run_loop(arguments: tuple[str, ...]) -> int:
    """Run each attempt in a fresh process so newly landed code is used."""
    executable = Path(sys.executable).parent / "chitty"
    if not executable.is_file():
        raise ChittyError(f"runner chitty executable not found: {executable}")
    while True:
        completed = subprocess.run([str(executable), "run", *arguments], check=False)
        keep_running, exit_code = loop_step(completed.returncode)
        if not keep_running:
            return exit_code
        time.sleep(RUN_LOOP_PAUSE_SECONDS)


def _run_agent(
    command: list[str], *, cwd: Path, env: dict[str, str], timeout: int
) -> subprocess.CompletedProcess[bytes]:
    """Wait for an agent, terminating its process tree when its deadline expires."""
    process = subprocess.Popen(command, cwd=cwd, env=env)
    try:
        process.wait(timeout=timeout or None)
    except subprocess.TimeoutExpired:
        descendants = _process_descendants(process.pid)
        for pid in [*descendants, process.pid]:
            _signal_process(pid, signal.SIGTERM)
        grace_deadline = time.monotonic() + AGENT_KILL_GRACE_SECONDS
        while time.monotonic() < grace_deadline:
            remaining = _running_processes([*descendants, process.pid])
            if not remaining:
                break
            time.sleep(min(0.05, grace_deadline - time.monotonic()))
        for pid in _running_processes([*descendants, process.pid]):
            _signal_process(pid, signal.SIGKILL)
        process.wait()
        return subprocess.CompletedProcess(command, process.returncode, stderr=b"timed out")
    return subprocess.CompletedProcess(command, process.returncode)


def _process_descendants(parent: int) -> list[int]:
    """Return descendants from the system process table in parent-first order."""
    result = subprocess.run(
        ["ps", "-A", "-o", "pid=", "-o", "ppid="], capture_output=True, text=True, check=True
    )
    parents: dict[int, list[int]] = {}
    for line in result.stdout.splitlines():
        pid, ppid = (int(value) for value in line.split())
        parents.setdefault(ppid, []).append(pid)
    found: list[int] = []
    pending = list(parents.get(parent, []))
    while pending:
        pid = pending.pop(0)
        found.append(pid)
        pending.extend(parents.get(pid, []))
    return found


def _running_processes(pids: list[int]) -> list[int]:
    """Return requested PIDs that still have a live process-table entry."""
    result = subprocess.run(
        ["ps", "-A", "-o", "pid=", "-o", "stat="], capture_output=True, text=True, check=True
    )
    states = {
        int(pid): state
        for line in result.stdout.splitlines()
        for pid, state in [line.split(maxsplit=1)]
    }
    return [pid for pid in pids if pid in states and not states[pid].startswith("Z")]


def _signal_process(pid: int, sig: signal.Signals) -> None:
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass


def _land_pending(main_repo: Repo) -> RunResult | None:
    """Retry completed local ticket branches before choosing new work."""
    tasks = {str(task.id).lower(): task.id for task in main_repo.all_tasks()}
    pending: list[StoredTask] = []
    for branch in git.local_branches(main_repo.root):
        task_id = tasks.get(branch)
        if task_id is None:
            continue
        stored = main_repo.find(task_id)
        if not stored.archived and stored.task.frontmatter.status == "done":
            pending.append(stored)
    pending.sort(key=lambda stored: stored.id)
    if not pending:
        return None
    setup = main_repo.config.setup
    check = main_repo.config.check
    assert setup is not None
    assert check is not None
    for stored in pending:
        task_id = stored.id
        action = NextAction("review", task_id)
        worktree = _worktree(main_repo.root, action, main_repo.config.main_branch)
        _land(main_repo, worktree, action, setup, check)
        print(f"landed {task_id}")
        return RunResult(action, "done", "done")
    raise AssertionError("unreachable")


def _lock_ticket(
    held: ExitStack,
    main_repo: Repo,
    ticket: str | None,
    modes: tuple[Literal["work", "review"], ...],
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
        action = next_action(main_repo, modes=modes, owner=owner)
        try:
            held.enter_context(
                locks.run_lock(main_repo.root, str(action.id), actor=actor(), mode=action.mode)
            )
        except locks.TicketLocked:
            # Another run locked it after `next_action` looked; it skips it now.
            continue
        return action
    action = next_action(main_repo, modes=modes, owner=owner)
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
        # After the merge, because the merge can change dependencies.
        _setup(setup, worktree)
    else:
        work_repo = Repo.open(worktree)
    if failed := _run_check(work_repo, worktree, action, check):
        return failed
    if action.mode == "review" and (blocked := _block_dirty_review(work_repo, worktree, action)):
        return blocked
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
                agent_environment = _command_environment()
                agent_environment["PATH"] = os.pathsep.join(
                    (str(runner_chitty.parent), agent_environment.get("PATH", ""))
                )
                try:
                    completed = _run_agent(
                        [
                            *agent_command,
                            *arguments,
                            *_model_arguments(main_repo, action, agent_command, arguments),
                        ],
                        cwd=worktree,
                        env=agent_environment,
                        timeout=main_repo.config.agent_timeout,
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
                timed_out = completed.stderr == b"timed out"
                outcome = agent_exit(completed.returncode, timed_out)
                if outcome == "interrupted":
                    raise RunInterrupted("agent")
                if outcome == "timed out":
                    raise ChittyError(
                        f"agent timed out after {main_repo.config.agent_timeout} seconds"
                    )
                if outcome == "failed":
                    raise ChittyError(f"agent exited with status {completed.returncode}")
                models = _read_usage(usage_file)
                usage_read = True

                # Pi commonly commits from this worktree. Reopen so history is re-read.
                new_status = _status_after_agent(main_root, worktree, action)
                status_result = status_outcome(old_status, new_status)
                if status_result == "unchanged":
                    raise ChittyError(
                        f"{action.id} was unchanged; only committed changes are visible "
                        "to `chitty run`"
                    )
                if status_result == "land":
                    _land(main_repo, worktree, action, setup, check)
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


def _model_arguments(
    repo: Repo, action: NextAction, command: tuple[str, ...], arguments: tuple[str, ...]
) -> tuple[str, ...]:
    """Supply the role default only when the command has no explicit model."""
    model = repo.config.work_model if action.mode == "work" else repo.config.review_model
    if model is None or any(
        word == "--model" or word.startswith("--model=") for word in (*command, *arguments)
    ):
        return ()
    return ("--model", model)


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
    """Merge the integration branch into a review ticket, or fail it back to its worker.

    The reviewer then sees exactly what would land. Returns the status change
    when the ticket fails here, so no review session is spent on it.
    """
    if blocked := _block_dirty_review(work_repo, worktree, action):
        return blocked
    try:
        conflicts = git.merge_main(worktree, main_branch)
    except KeyboardInterrupt:
        if git.merge_in_progress(worktree):
            git.abort_merge(worktree)
        raise RunInterrupted("merge") from None
    if conflicts:
        listed = ", ".join(f"`{path}`" for path in conflicts)
        return _fail_review(
            work_repo,
            action,
            f"Review failed (integration): merging `{main_branch}` conflicts in {listed}.",
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


def _block_dirty_review(work_repo: Repo, worktree: Path, action: NextAction) -> RunResult | None:
    if not (uncommitted := git.uncommitted_paths(worktree)):
        return None
    listed = ", ".join(f"`{path}`" for path in uncommitted)
    old_status = work_repo.find(action.id).task.frontmatter.status
    change = work_repo.edit(
        action.id,
        Edit(
            status="blocked",
            owner="human",
            note="Review blocked (work): the worktree has uncommitted changes: "
            f"{listed}. A human must resolve the files and decide when to resume.",
            skip_verdicts=True,
        ),
    )
    return RunResult(action, old_status, change.task.task.frontmatter.status)


def _changed_agents_block(worktree: Path, main_branch: str | None = None) -> bool:
    """Return whether the branch changes or damages the managed guide block."""
    if main_branch is None:
        main_branch = Repo.open(git.main_checkout(worktree)).config.main_branch
    agents = worktree / AGENTS_FILE
    branch_text = agents.read_text() if agents.exists() else None
    main_text = git.file_at_merge_base(worktree, main_branch, "HEAD", AGENTS_FILE)
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
    """Return the Chitty config path when the merged branch changed it."""
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
    # An unfinished operation needs a person, not a second worktree. Its own
    # `.git` file means a stray directory never reads the main checkout's state.
    if (destination / ".git").exists():
        if git.merge_in_progress(destination):
            raise ChittyError(
                f"{destination} has an unfinished merge; finish it or run `git merge --abort` there"
            )
        if git.rebase_in_progress(destination):
            raise ChittyError(
                f"{destination} has an unfinished rebase; finish it or run "
                "`git rebase --abort` there"
            )
    existing = git.worktree_for_branch(main_root, branch)
    if existing is not None:
        if existing.resolve() == main_root.resolve():
            raise ChittyError(f"branch {branch} is checked out in the main checkout")
        if git.merge_in_progress(existing):
            raise ChittyError(
                f"{existing} has an unfinished merge; finish it or run `git merge --abort` there"
            )
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


def _land(main_repo: Repo, worktree: Path, action: NextAction, setup: str, check: str) -> None:
    """Serialize landing operations that mutate the shared main branch."""
    with locks.landing_lock(main_repo.root):
        try:
            _land_locked(main_repo, worktree, action, setup, check)
        except ChittyError as exc:
            raise ChittyError(
                f"{exc}\nA human must resolve the landing problem in {worktree} "
                "or the main checkout before retrying."
            ) from exc


def _land_locked(
    main_repo: Repo, worktree: Path, action: NextAction, setup: str, check: str
) -> None:
    """Land a completed ticket and remove its linked worktree."""
    main_root = main_repo.root
    branch = str(action.id).lower()
    # A prior run or a reviewer may already have removed this ticket entirely.
    if not git.has_local_branch(main_root, branch) and not worktree.exists():
        return
    main_branch = main_repo.config.main_branch
    if git.current_branch(main_root) != main_branch:
        raise ChittyError(f"the main checkout must be on branch {main_branch} to land a ticket")
    git.require_clean(main_root)
    # A session may have landed its own ticket before returning.
    if not worktree.exists():
        return
    if uncommitted := git.uncommitted_paths(worktree):
        listed = ", ".join(f"`{path}`" for path in uncommitted)
        raise ChittyError(
            f"cannot land {action.id}; its worktree has uncommitted changes: {listed}"
        )
    if changed := _changed_config(worktree, main_branch):
        raise ChittyError(
            f"cannot land {action.id}; the branch changes `{changed}`; "
            "only `chitty init` on the main checkout may change it"
        )
    if _changed_agents_block(worktree, main_branch):
        raise ChittyError(
            f"cannot land {action.id}; the branch changes Chitty's managed block in AGENTS.md"
        )
    if conflicts := git.merge(worktree, main_branch):
        listed = ", ".join(f"`{path}`" for path in conflicts)
        raise ChittyError(f"cannot land {action.id}; merging `{main_branch}` conflicts in {listed}")
    if changed := _changed_config(worktree, main_branch):
        raise ChittyError(
            f"cannot land {action.id}; the merged branch changes `{changed}`; "
            "only `chitty init` on the main checkout may change it"
        )
    _setup(setup, worktree)
    _landing_check(check, worktree)
    git.fast_forward(main_root, branch)
    git.remove_worktree(main_root, worktree)
    git.delete_branch(main_root, branch)


def _landing_check(command: str, worktree: Path) -> None:
    """Run landing validation without changing the ticket on failure."""
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=worktree,
            stdin=subprocess.DEVNULL,
            env=_command_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise ChittyError(f"landing check command not found: {command}") from None
    except KeyboardInterrupt:
        raise RunInterrupted("check") from None
    if completed.returncode:
        lines = completed.stdout.splitlines()[-20:]
        output = "\n".join(lines) or "(no output)"
        raise ChittyError(f"landing check exited with status {completed.returncode}:\n{output}")


def _setup(command: str, worktree: Path) -> None:
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=worktree,
            stdin=subprocess.DEVNULL,
            env=_command_environment(),
            check=False,
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
            env=_command_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        output = f"check command not found: {command}"
        return _handle_check_failure(work_repo, action, output)
    except KeyboardInterrupt:
        raise RunInterrupted("check") from None
    if completed.returncode == 0:
        return None
    lines = completed.stdout.splitlines()[-20:]
    output = "\n".join(lines) or "(no output)"
    detail = f"check exited with status {completed.returncode}:\n{_code_block(output)}"
    return _handle_check_failure(work_repo, action, detail)


def _code_block(text: str) -> str:
    """Fence command output so a note cannot read it as Markdown structure."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def _handle_check_failure(work_repo: Repo, action: NextAction, detail: str) -> RunResult | None:
    if action.mode == "work":
        status = work_repo.find(action.id).task.frontmatter.status
        if status == "todo":
            raise ChittyError(f"check failed before {action.id} started: {detail}")
        work_repo.edit(
            action.id,
            Edit(note=f"Check failed before this session: {detail}", skip_verdicts=True),
        )
        return None
    if blocked := _block_dirty_review(work_repo, work_repo.root, action):
        return blocked
    return _fail_check(work_repo, action, detail)


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
