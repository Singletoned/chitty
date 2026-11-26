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
from collections.abc import Sequence
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Literal
from uuid import uuid4

from chitty import git, locks
from chitty.actor import actor, run_actor
from chitty.commands import (
    CommandTimedOut,
    code_block,
    command_environment,
    run_git,
    run_logged,
    terminate_process_tree,
)
from chitty.config import (
    BACKLOG_DIR,
    CHITTY_VERSION,
    CONFIG_NAME,
    PYPROJECT_NAME,
    config_source,
    git_common_dir,
    landing_command,
    usage_path,
    version_key,
)
from chitty.errors import NO_NEXT_TICKET_EXIT, ChittyError, ManagedGuideError, NoNextTicket
from chitty.git import has_work_beyond_tickets
from chitty.ids import ID_RE, TaskId
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
LANDING_LOG_TAIL_LINES = 40
LANDING_ATTEMPTS = 3
QUICK_LANDING_ATTEMPTS = 10
RUN_LOOP_PAUSE_SECONDS = 60
# An agent that leaves its ticket unchanged is continued this many times at most.
MAX_CONTINUATIONS = 5
AGENT_OUTPUT_TAIL_LINES = 40
CONTINUE_ARGUMENT = "-c"  # Each agent CLI's flag for resuming its latest session.


class LandingCheckFailed(ChittyError):
    """The landing check ran and exited unsuccessfully."""


# Used by the work runner when its rebase integration lands.
def _rebase_work_worktree(
    worktree: Path, task_id: TaskId, main_branch: str, *, stop_on_conflict: bool
) -> bool:
    ref = f"refs/chitty/stash/{task_id}"
    saved = git.save_work(worktree, ref, f"chitty {task_id} before rebase")
    try:
        unresolved = git.rebase_onto(worktree, main_branch)
    except ChittyError:
        if saved:
            git.restore_work(worktree, ref)
        raise
    if unresolved:
        ticket_paths = [path for path in unresolved if str(path).startswith(f"{BACKLOG_DIR}/")]
        if stop_on_conflict and not ticket_paths:
            return True
        git.abort_rebase(worktree)
        if saved:
            git.restore_work(worktree, ref)
        if stop_on_conflict and ticket_paths:
            raise ChittyError(
                f"rebase onto {main_branch} conflicts in ticket files: {ticket_paths}"
            )
        return False
    if saved:
        git.restore_work(worktree, ref)
    return False


def _has_work(paths: Sequence[PurePosixPath]) -> bool:
    return any(len(path.parts) < 2 or path.parts[0] != BACKLOG_DIR for path in paths)


def _branch_has_work(worktree: Path, main_branch: str) -> bool:
    return _has_work(git.changed_paths(worktree, main_branch, "HEAD"))


def _only_ticket_paths(paths: Sequence[str], contexts: Sequence[str]) -> bool:
    """Whether paths are all beneath a configured context's ticket directory."""
    directories = tuple(f"chitty/{name}/" for name in contexts)
    return all(path.startswith(directories) for path in paths)


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


class RunInterrupted(Exception):
    """The user interrupted a `chitty run` phase; the command must stop a shell loop."""

    def __init__(self, phase: str) -> None:
        self.phase = phase


class AgentSessionFailed(ChittyError):
    """An agent session exited unsuccessfully."""


class AgentStartFailed(ChittyError):
    """An agent failed without committing work."""


class RepairError(ChittyError):
    """A repair agent finished without reaching an accepted final status."""


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
    modes: tuple[Literal["work", "review", "errors"], ...] = (),
    owner: str | None = None,
) -> RunResult:
    """Prepare the selected ticket and run Pi with inherited streams."""
    # Set identity before validating arguments or selecting a ticket so this
    # command also works when launched from an ordinary human shell.
    os.environ.pop("CHITTY_ACTOR", None)
    os.environ["CHITTY_ACTOR"] = run_actor(str(uuid4()))
    main_repo = repo
    context: dict[str, Any] = {
        "actor": actor(),
        "phase": "startup",
        "ticket": None,
        "mode": None,
        "worktree": None,
    }
    try:
        if modes and ticket is not None:
            # A named ticket already decides its mode, so a mode could only disagree.
            raise ChittyError("--mode cannot be used with --ticket")
        if ticket is not None and owner is not None:
            raise ChittyError("--owner cannot be used with --ticket")
        if owner in ("", "human"):
            raise ChittyError("--owner must name an agent, not human or empty")
    except ChittyError as error:
        report_error(main_repo, error, context)
        raise
    try:
        main_root = git.main_checkout(repo.root)
        main_repo = Repo.open(main_root)
        _refuse_stale_linked_worktree(repo, main_repo)
        context["phase"] = "preflight"
        _preflight(main_repo, agent)
        main_repo.refresh_setup()
        project = main_repo.config.project
        if project is None:
            raise ChittyError("`chitty run` requires a project name after setup refresh")
        context["project"] = project

        with locks.landing_lock(main_repo.root):
            _remove_merged_branches(main_repo)

        if ticket is None:
            landed = _land_pending(main_repo)
            if landed is not None:
                return landed

        with ExitStack() as held:
            context["phase"] = "selection"
            action = _lock_ticket(held, main_repo, ticket, modes, owner)
            context.update(ticket=str(action.id), mode=action.mode, phase="ticket")
            return _run_ticket(main_repo, project, action, arguments, agent, context)
    except RunInterrupted as interrupted:
        report_error(
            main_repo,
            ChittyError(f"interrupted during {interrupted.phase}"),
            {**context, "phase": interrupted.phase},
        )
        raise
    except ChittyError as error:
        if not isinstance(error, NoNextTicket):
            report_error(main_repo, error, context)
        raise


def render_command(words: Sequence[str], mode: str, ticket_id: str, prompt: str) -> tuple[str, ...]:
    """Expand command words in order, keeping placeholder text in prompt literal."""
    return tuple(
        os.path.expanduser(word)
        .replace("{mode}", mode)
        .replace("{id}", ticket_id)
        .replace("{prompt}", prompt)
        for word in words
    )


_PLACEHOLDER = re.compile(r"\{(message|context)\}")


def report_error(repo: Repo, error: ChittyError, context: dict[str, Any]) -> None:
    """Run `error_reporter`; a failing reporter warns without replacing `error`."""
    command = repo.config.error_reporter
    if command is None:
        return
    values = {"message": str(error), "context": json.dumps(context, sort_keys=True)}
    try:
        argv = [
            _PLACEHOLDER.sub(lambda match: values[match.group(1)], word)
            for word in shlex.split(command)
        ]
        completed = subprocess.run(argv, check=False, env=command_environment())
    except (OSError, ValueError) as reporter_error:
        print(f"warning: error_reporter did not run: {reporter_error}", file=sys.stderr)
        return
    if completed.returncode:
        print(
            f"warning: error_reporter exited with status {completed.returncode}",
            file=sys.stderr,
        )


def _loop_rule(label: str) -> str:
    """Format a terminal-width rule for one loop event."""
    title = f"━━━━ {label} "
    return title + "━" * max(0, shutil.get_terminal_size().columns - len(title))


def run_loop(arguments: tuple[str, ...]) -> int:
    """Run each attempt in a fresh process so newly landed code is used."""
    executable = Path(sys.executable).parent / "chitty"
    if not executable.is_file():
        raise ChittyError(f"runner chitty executable not found: {executable}")
    while True:
        print(_loop_rule(f"chitty run · {datetime.now():%H:%M:%S}"), file=sys.stderr)
        completed = subprocess.run([str(executable), "run", *arguments], check=False)
        keep_running, exit_code = loop_step(completed.returncode)
        if not keep_running:
            print(_loop_rule(f"stopped · exit {exit_code}"), file=sys.stderr)
            return exit_code
        # Schedule from completion, so attempt duration does not shorten the wait.
        next_run = datetime.now() + timedelta(seconds=RUN_LOOP_PAUSE_SECONDS)
        outcome = "no ticket" if completed.returncode == NO_NEXT_TICKET_EXIT else "finished"
        print(
            _loop_rule(f"{outcome} · next run at {next_run:%H:%M:%S}"),
            file=sys.stderr,
        )
        time.sleep(RUN_LOOP_PAUSE_SECONDS)


def _run_agent(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    log: BinaryIO,
) -> subprocess.CompletedProcess[bytes]:
    """Write merged agent output to log, terminating timed-out process trees."""
    log.flush()
    log.seek(0, os.SEEK_END)
    offset = log.tell()
    process = subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
    timed_out = False
    try:
        process.wait(timeout=timeout or None)
    except subprocess.TimeoutExpired:
        timed_out = True
        terminate_process_tree(process)

    end = os.fstat(log.fileno()).st_size
    log.seek(offset)
    output = log.read(end - offset)
    result = subprocess.CompletedProcess(command, process.returncode, stdout=output)
    if timed_out:
        result.stderr = b"timed out"
    return result


def _remove_merged_branches(main_repo: Repo) -> None:
    """Remove clean linked worktrees for local ticket branches contained by main."""
    root = main_repo.root
    # A missing worktree directory leaves stale metadata; prune before looking up branches.
    git.prune_worktrees(root)
    prefixes = tuple(f"{context.prefix.lower()}-" for context in main_repo.config.contexts.values())
    main_tip = main_repo.config.main_branch
    for branch in git.local_branches(root):
        if not branch.startswith(prefixes) or not ID_RE.fullmatch(branch):
            continue
        if not git.is_ancestor(root, branch, main_tip):
            continue
        task_id = branch.upper()
        stored = main_repo.lookup(TaskId.parse(task_id))
        worktree = git.worktree_for_branch(root, branch)
        reason = None
        if stored is not None and not stored.archived and stored.task.frontmatter.status != "done":
            reason = f"{task_id} is {stored.task.frontmatter.status}"
        elif locks.is_locked(root, task_id):
            reason = "run lock is held"
        elif worktree is not None and worktree.resolve() == root.resolve():
            reason = "is the main checkout"
        elif worktree is not None and git.uncommitted_paths(worktree):
            reason = "worktree has uncommitted changes"
        elif worktree is not None and git.rebase_in_progress(worktree):
            reason = "rebase in progress"
        elif worktree is not None and git.merge_in_progress(worktree):
            reason = "merge in progress"
        if reason:
            print(f"kept merged branch {branch}: {reason}", file=sys.stderr)
            continue
        try:
            if worktree is not None:
                git.remove_worktree(root, worktree)
            git.delete_branch(root, branch)
        except ChittyError as error:
            print(f"kept merged branch {branch}: {error}", file=sys.stderr)
            continue
        print(f"removed merged branch {branch}", file=sys.stderr)


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
            if stored.branch != branch:
                print(
                    f"not landing {branch}: {task_id} is read from {stored.branch}", file=sys.stderr
                )
                continue
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
        if _land(
            main_repo,
            worktree,
            action,
            setup,
            landing_command(main_repo.config.check, main_repo.config.landing_check),
        ):
            print(f"landed {task_id}")
            return RunResult(action, "done", "done")
    return None


def _lock_ticket(
    held: ExitStack,
    main_repo: Repo,
    ticket: str | None,
    modes: tuple[Literal["work", "review", "errors"], ...],
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


def log_path(git_common_dir: Path, ticket_id: TaskId, now: datetime) -> Path:
    """Return the persistent agent log path for a UTC run timestamp."""
    utc = now.astimezone(UTC)
    stamp = f"{utc.year:04d}{utc:%m%d%H%M%S%f}Z"
    return git_common_dir / "chitty" / "run" / f"{ticket_id}-{stamp}.log"


def _run_ticket(
    main_repo: Repo,
    project: str,
    action: NextAction,
    arguments: tuple[str, ...],
    agent: str | None,
    context: dict[str, Any],
) -> RunResult:
    """Own the persistent agent log for one locked ticket attempt."""
    common_dir = git_common_dir(main_repo.root)
    if common_dir is None:
        raise ChittyError(f"{main_repo.root} is not in a Git repository")
    path = log_path(common_dir, action.id, datetime.now(UTC))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        log = path.open("x+b")
    except OSError as error:
        raise ChittyError(f"cannot create agent log {path}: {error}") from error
    try:
        with log, tempfile.TemporaryDirectory(prefix="chitty-agent-") as bin_dir:
            return _run_ticket_with_log(
                main_repo, project, action, arguments, agent, context, log, Path(bin_dir)
            )
    finally:
        print(f"log: {display_path(path, main_repo.root)}", file=sys.stderr)


def _agent_path(environment: dict[str, str], bin_dir: Path) -> None:
    """Expose only the runner's Chitty executable to the agent."""
    executable = Path(sys.executable).parent / "chitty"
    if not executable.is_file():
        raise ChittyError(f"runner chitty executable not found: {executable}")
    (bin_dir / "chitty").symlink_to(executable.absolute())
    environment["PATH"] = os.pathsep.join((str(bin_dir), environment.get("PATH", "")))


def _run_ticket_with_log(
    main_repo: Repo,
    project: str,
    action: NextAction,
    arguments: tuple[str, ...],
    agent: str | None,
    context: dict[str, Any],
    log: BinaryIO,
    bin_dir: Path,
) -> RunResult:
    """Prepare the locked ticket's worktree and run its agent."""
    main_root = main_repo.root
    stored = main_repo.find(action.id)
    selected_status = stored.task.frontmatter.status
    repairing = selected_status == "error"
    agent_environment = command_environment()
    planned_worktree = main_root / ".worktrees" / str(action.id).lower()
    agent_command = _agent_command(
        main_repo, action, agent, worktree=planned_worktree, mode=action.mode
    )
    if action.mode == "review":
        branch = str(action.id).lower()
        existing_worktree = git.worktree_for_branch(main_root, branch)
        if existing_worktree is None and not git.has_local_branch(main_root, branch):
            note = f"Runner error (review): {action.id} has no branch `{branch}` and no worktree."
            change = main_repo.edit(
                action.id,
                Edit(
                    status="error",
                    note=note,
                    skip_verdicts=True,
                    skip_current_version=True,
                ),
            )
            return RunResult(action, "review", change.task.task.frontmatter.status)
    existing_worktree = git.worktree_for_branch(main_root, str(action.id).lower())
    relative_ticket = stored.path.relative_to(main_root)
    if existing_worktree is not None and git.dirty_paths(existing_worktree, relative_ticket):
        raise ChittyError(f"{existing_worktree / relative_ticket} has uncommitted changes")
    worktree = _worktree(main_root, action, main_repo.config.main_branch)
    stopped = False
    if action.mode == "work":
        try:
            stopped = _rebase_work_worktree(
                worktree,
                action.id,
                main_repo.config.main_branch,
                stop_on_conflict=selected_status in ("doing", "error")
                and not git.uncommitted_paths(worktree),
            )
        except ChittyError as error:
            return _record_ticket_error(Repo(worktree, main_repo.config), action, "rebase", error)
    context["worktree"] = str(worktree)
    branch_repo = Repo(worktree, main_repo.config)
    if action.mode == "work" and not stopped:
        ref = f"refs/chitty/stash/{action.id}"
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            branch_repo.edit(
                action.id,
                Edit(
                    note=(
                        "Uncommitted changes from before the rebase did not apply cleanly; "
                        f"they are in {ref}."
                    ),
                    skip_verdicts=True,
                    skip_current_version=True,
                ),
            )
        elif result.returncode != 1:
            raise subprocess.CalledProcessError(result.returncode, result.args)
    if action.mode == "work" and selected_status == "todo" and not stopped:
        branch_repo.edit(
            action.id,
            Edit(status="doing", skip_verdicts=True, skip_current_version=True),
        )
    agent_command = _agent_command(
        Repo(worktree, main_repo.config), action, agent, worktree=worktree, mode=action.mode
    )
    setup = main_repo.config.setup
    check = main_repo.config.check
    assert setup is not None  # `_preflight` rejects an unset setup command.
    assert check is not None  # `_preflight` rejects an unset check command.
    if action.mode == "work" and not stopped:
        context["phase"] = "setup"
        try:
            _setup(setup, worktree, main_repo.config.command_timeout)
        except ChittyError as error:
            failed = _record_ticket_error(branch_repo, action, "setup", error)
            return RunResult(action, selected_status, failed.new_status)

    if action.mode == "review":
        context["phase"] = "review preparation"
        # The config may be deleted on a branch, so use main's config until the
        # review preflight has confirmed that the branch still has one.
        work_repo = Repo(worktree, main_repo.config)
        # The run's own actor never worked on the ticket, so it may fail it.
        context["phase"] = "review preparation"
        try:
            _agent_path(agent_environment, bin_dir)
        except ChittyError as error:
            failed = _record_ticket_error(work_repo, action, "review preparation", error)
            return RunResult(action, selected_status, failed.new_status)
        failed = _prepare_review(
            work_repo,
            worktree,
            action,
            main_repo.config.main_branch,
            agent,
            project,
            agent_environment,
            log,
        )
        if failed is not None:
            return failed
        work_repo = Repo.open(worktree)
        # After the merge, because the merge can change dependencies.
        context["phase"] = "setup"
        try:
            _setup(setup, worktree, main_repo.config.command_timeout)
        except ChittyError as error:
            return _record_ticket_error(branch_repo, action, "setup", error)
    else:
        work_repo = Repo.open(worktree)
    context["phase"] = "check"
    if not stopped and (
        failed := _run_check(
            branch_repo, main_root, action, check, selected_status, main_repo.config.command_timeout
        )
    ):
        if action.mode == "work" and selected_status == "todo":
            return RunResult(action, selected_status, failed.new_status)
        return failed
    if action.mode == "review" and (blocked := _block_dirty_review(work_repo, worktree, action)):
        return blocked
    old_status = work_repo.find(action.id).task.frontmatter.status
    started = datetime.now(UTC)
    elapsed_start = time.monotonic()
    new_status: str | None = None
    handoff: RunResult | None = None
    context["phase"] = "agent"
    print(f"Check passed; {action.mode} agent is working on {action.id}...", file=sys.stderr)
    try:
        if action.mode != "review":
            agent_environment = command_environment()
            _agent_path(agent_environment, bin_dir)
        head = run_git(worktree, "rev-parse", "HEAD").strip()
        try:
            new_status = _agent_sessions(
                main_repo,
                action,
                agent,
                agent_command,
                arguments,
                worktree,
                agent_environment,
                "error" if repairing else old_status,
                log,
            )
        except AgentSessionFailed as error:
            if run_git(worktree, "rev-parse", "HEAD").strip() != head:
                raise
            repo = Repo(worktree, main_repo.config)
            if repo.find(action.id).task.frontmatter.status != selected_status:
                repo.edit(
                    action.id,
                    Edit(status=selected_status, skip_verdicts=True, skip_current_version=True),
                )
            raise AgentStartFailed(
                f"agent failed before committing anything; {action.id} left at "
                f"{selected_status}: {error}"
            ) from error
        if repairing and new_status not in {"review", "blocked"}:
            raise RepairError(
                f"repair agent left {action.id} in invalid status {new_status}; "
                "expected review or blocked"
            )
        if repairing:
            if new_status == "review":
                changed = git.changed_paths(
                    worktree, main_repo.config.main_branch, str(action.id).lower()
                )
                ticket_directories = (
                    PurePosixPath(context.directory.relative_to(main_root).as_posix())
                    for context in main_repo.contexts()
                )
                if not has_work_beyond_tickets(changed, ticket_directories):
                    raise RepairError(
                        f"repair agent returned {action.id} to review with no change beyond "
                        "its ticket files"
                    )
            if new_status == "blocked":
                # Keep the repair outcome on its ticket branch; the agent's note
                # remains first, followed by the runner's handoff context.
                work_repo = Repo(worktree, main_repo.config)
                work_repo.edit(
                    action.id,
                    Edit(
                        note="Repair agent determined that human action is required.",
                        skip_verdicts=True,
                        skip_current_version=True,
                    ),
                )
        if status_outcome(old_status, new_status) == "land":
            context["phase"] = "landing"
            _land(
                main_repo,
                worktree,
                action,
                setup,
                landing_command(main_repo.config.check, main_repo.config.landing_check),
            )
    except RunInterrupted:
        raise
    except (RepairError, AgentStartFailed):
        raise
    except LandingCheckFailed as error:
        old = branch_repo.find(action.id).task.frontmatter.status
        tail = "\n".join((worktree / ".chitty/check.log").read_text().splitlines()[-LANDING_LOG_TAIL_LINES:])
        note = (f"Review failed (integration): after rebasing onto `main`, the landing check failed: {error}"
                f"\n\n{code_block(tail)}\n\nWorktree: `{worktree}`")
        change = branch_repo.edit(action.id, Edit(status="doing", note=note, skip_verdicts=True, skip_current_version=True))
        handoff = RunResult(action, old, change.task.task.frontmatter.status)
    except ChittyError as error:
        handoff = _record_ticket_error(branch_repo, action, context["phase"], error)
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
            },
        )
    if handoff is not None:
        return handoff
    assert new_status is not None
    return RunResult(action, old_status, new_status)


def continuation_step(progress: Sequence[bool], cap: int) -> Literal["continue", "stop"]:
    """Stop after more than cap consecutive idle sessions."""
    return "stop" if len(progress) > cap and not any(progress[-(cap + 1):]) else "continue"


def stalled_agent_message(first_line: str, seconds: int, returncode: int, output: str) -> str:
    """Describe the last session of a stalled agent."""
    tail = output.splitlines()[-AGENT_OUTPUT_TAIL_LINES:] if output else ["(no output)"]
    return "\n".join([first_line, f"last session: exit {returncode} after {seconds}s", *tail])


def _agent_sessions(
    main_repo: Repo,
    action: NextAction,
    agent: str | None,
    agent_command: tuple[str, ...],
    arguments: tuple[str, ...],
    worktree: Path,
    environment: dict[str, str],
    old_status: str,
    log: BinaryIO,
) -> str:
    """Run the agent, continuing it while its ticket stays unchanged; return the new status."""
    continuations = 0
    progress: list[bool] = []
    ticket_directories = [PurePosixPath(context.directory.relative_to(main_repo.root).as_posix())
                          for context in main_repo.contexts()]
    command = agent_command
    while True:
        continuing = continuations > 0
        before = git.ref_commit(worktree, "HEAD")
        completed, seconds = _run_session(
            main_repo,
            action,
            command,
            arguments,
            worktree,
            environment,
            continuing,
            action.mode,
            log,
        )
        # Pi commonly commits from this worktree. Reopen so history is re-read.
        new_status = _status_after_agent(main_repo.root, worktree, action)
        if old_status == "error" and new_status == "error":
            return new_status
        if status_outcome(old_status, new_status) != "unchanged":
            return new_status
        after = git.ref_commit(worktree, "HEAD")
        progress.append(bool(before and after and before != after and has_work_beyond_tickets(
            git.paths_between(worktree, before, after), ticket_directories
        )))
        if continuation_step(progress, MAX_CONTINUATIONS) == "stop" or not _accepts_prompt(main_repo, agent):
            idle = 0
            for made_progress in reversed(progress[:-1]):
                if made_progress:
                    break
                idle += 1
            first_line = (
                f"{action.id} is still `{new_status}` after {idle} continuations with no new work committed; "
                "only committed changes are visible to `chitty run`"
            )
            output = completed.stdout.decode(errors="replace") if completed.stdout else ""
            raise ChittyError(stalled_agent_message(first_line, seconds, completed.returncode, output))
        continuations += 1
        command = _agent_command(
            main_repo, action, agent, worktree=worktree, mode=action.mode, continuation=True
        )


def _run_session(
    repo: Repo,
    action: NextAction,
    command: tuple[str, ...],
    arguments: tuple[str, ...],
    worktree: Path,
    environment: dict[str, str],
    continuing: bool,
    mode: str,
    log: BinaryIO,
) -> tuple[subprocess.CompletedProcess[bytes], int]:
    """Run one agent session; raise unless it exits 0 within `agent_timeout`."""
    session = [*command, *arguments, *_model_arguments(repo, mode, command, arguments)]
    if continuing:
        session.append(CONTINUE_ARGUMENT)
    try:
        started = time.monotonic()
        completed = _run_agent(
            session,
            cwd=worktree,
            env=environment,
            timeout=repo.config.agent_timeout,
            log=log,
        )
    except FileNotFoundError:
        raise AgentSessionFailed(f"agent command not found: {command[0]}") from None
    except KeyboardInterrupt:
        raise RunInterrupted("agent") from None
    seconds = round(time.monotonic() - started)
    timed_out = completed.stderr == b"timed out"
    outcome = agent_exit(completed.returncode, timed_out)
    if outcome == "interrupted":
        raise RunInterrupted("agent")
    if outcome == "timed out":
        output = completed.stdout.decode(errors="replace") if completed.stdout else "(no output)"
        raise ChittyError(f"agent timed out after {repo.config.agent_timeout} seconds:\n{output}")
    if outcome == "failed":
        output = completed.stdout.decode(errors="replace") if completed.stdout else "(no output)"
        raise AgentSessionFailed(f"agent exited with status {completed.returncode}:\n{output}")
    return completed, seconds


def continuation_prompt(mode: Literal["work", "review"], ticket_id: str) -> str:
    """Return the prompt that resumes an agent session which left its ticket unfinished."""
    if mode == "work":
        return (
            f"Continue working only on Chitty ticket {ticket_id}. Either finish it and set "
            "it to `review`, return it to `planning` for a defect in the ticket with a note "
            "explaining the problem and decision needed, or set it to `blocked` with a note "
            "giving the "
            "external obstacle. There is no token, time or context budget, so none is an "
            "obstacle; a ticket too large for one session goes to `planning` with a note "
            "proposing a split. Do not stop with it unfinished."
        )
    return (
        f"Continue reviewing only Chitty ticket {ticket_id}. Either pass it (`done`) or "
        "fail it (`doing`, with the failures in one note), return it to `planning` for "
        "a defect in the ticket with a review note explaining the problem and decision "
        "needed, or set it "
        "to `blocked` with a note giving the external obstacle. Keep one verdict per "
        "criterion. Do not merge or remove branches or worktrees."
    )


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


def _preflight(repo: Repo, agent: str | None) -> None:
    source = config_source(repo.root)
    assert source is not None  # `Repo.open` rejects repositories without config.
    config_file = source.relative_to(repo.root)
    problems: list[str] = []
    if not repo.config.autocommit:
        problems.append(
            f"`chitty run` requires `autocommit = true` in {config_file}, "
            "so ticket changes reach every branch; `chitty init --autocommit` sets it"
        )
    if repo.config.setup is None:
        problems.append(
            f"`chitty run` requires `setup` in {config_file}: the command that installs "
            "a new ticket worktree's environment before the agent starts, for example "
            'setup = "make install"'
        )
    if repo.config.check is None:
        problems.append(
            f"`chitty run` requires `check` in {config_file}: the command that validates "
            'a ticket worktree before the agent starts, for example check = "make check"'
        )
    if agent is None and not (repo.config.agent_command or "").strip():
        problems.append(
            'agent_command is the default agent command; example: agent_command = "pi -p {prompt}"'
        )
    if problems:
        details = "\n".join(f"- {problem}" for problem in problems)
        raise ChittyError(f"`chitty run` configuration is incomplete in {config_file}:\n{details}")
    if git.current_branch(repo.root) != repo.config.main_branch:
        raise ChittyError(f"the main checkout must be on branch {repo.config.main_branch}")


def _model_arguments(
    repo: Repo, mode: str, command: tuple[str, ...], arguments: tuple[str, ...]
) -> tuple[str, ...]:
    """Supply the mode default only when the command has no explicit model."""
    model_settings = {
        "work": repo.config.work_model,
        "review": repo.config.review_model,
        "rebase": repo.config.rebase_model,
    }
    if mode not in model_settings:
        raise ChittyError(f"unknown session mode {mode!r}")
    model = model_settings[mode]
    if model is None or any(
        word == "--model" or word.startswith("--model=") for word in (*command, *arguments)
    ):
        return ()
    return ("--model", model)


def _agent_setting(repo: Repo, agent: str | None) -> tuple[str, str]:
    """Return the setting name and command text of the selected agent."""
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
    example = 'agent_command = "pi -p {prompt}"'
    if command is None or not command.strip():
        if setting == "agent_command":
            raise ChittyError(f"`chitty run` requires agent_command; for example: {example}")
        raise ChittyError(f"`chitty run` requires {setting}")
    return setting, command


def _accepts_prompt(repo: Repo, agent: str | None) -> bool:
    """Whether the selected command takes `{prompt}`, which only continuation supports."""
    return "{prompt}" in _agent_setting(repo, agent)[1]


def _agent_command(
    repo: Repo,
    action: NextAction,
    agent: str | None,
    worktree: Path,
    mode: str,
    continuation: bool = False,
) -> tuple[str, ...]:
    """Parse and validate the selected command after setup refreshes it."""
    setting, command = _agent_setting(repo, agent)
    try:
        words = shlex.split(command)
    except ValueError as error:
        raise ChittyError(f"invalid {setting}: {error}") from None
    if mode == "rebase" and "{prompt}" not in command:
        raise ChittyError("the rebase session needs {prompt} in agent_command")
    if ("{mode}" not in command or "{id}" not in command) and "{prompt}" not in command:
        raise ChittyError(f"{setting} must contain both {{mode}} and {{id}}, or {{prompt}}")
    prompt = ""
    if "{prompt}" in command:
        ticket = str(action.id)
        if continuation:
            prompt = continuation_prompt(action.mode, ticket)
        elif mode == "rebase":
            prompt = guide(
                "rebase",
                ticket,
                directory=worktree if worktree.is_dir() else repo.root,
                workflow=repo.config.workflow,
            )
        elif repo.find(action.id).task.frontmatter.status == "error":
            prompt = guide(
                "repair",
                ticket,
                directory=worktree if worktree.is_dir() else repo.root,
                workflow=repo.config.workflow,
            )
        else:
            prompt = guide(
                mode,
                ticket,
                directory=worktree if worktree.is_dir() else repo.root,
                workflow=repo.config.workflow,
            )
    is_repair = repo.find(action.id).task.frontmatter.status == "error"
    command_mode = mode if mode == "rebase" else "repair" if is_repair else mode
    rendered = render_command(words, command_mode, str(action.id), prompt)
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
    work_repo: Repo,
    worktree: Path,
    action: NextAction,
    main_branch: str,
    agent: str | None,
    project: str,
    environment: dict[str, str],
    log: BinaryIO,
) -> RunResult | None:
    """Rebase a review ticket onto main, or fail it back to its worker.

    The reviewer then sees exactly what would land. Returns the status change
    when the ticket fails here, so no review session is spent on it.
    """
    if blocked := _block_dirty_review(work_repo, worktree, action):
        return blocked
    try:
        conflicts = git.rebase_onto(worktree, main_branch)
    except KeyboardInterrupt:
        if git.rebase_in_progress(worktree):
            git.abort_rebase(worktree)
        raise RunInterrupted("rebase") from None
    if conflicts:
        listed = ", ".join(f"`{path}`" for path in conflicts)
        old_status = work_repo.find(action.id).task.frontmatter.status
        started = datetime.now(UTC)
        elapsed_start = time.monotonic()
        failure: str | None = None
        try:
            command = _agent_command(work_repo, action, agent, worktree=worktree, mode="rebase")
            _run_session(
                work_repo, action, command, (), worktree, environment, False, "rebase", log
            )
            if git.rebase_in_progress(worktree):
                raise ChittyError("rebase still in progress")
            if uncommitted := git.uncommitted_paths(worktree):
                raise ChittyError(", ".join(f"`{path}`" for path in uncommitted))
        except (RunInterrupted, KeyboardInterrupt):
            if git.rebase_in_progress(worktree):
                git.abort_rebase(worktree)
            raise RunInterrupted("rebase") from None
        except ChittyError as error:
            failure = str(error).splitlines()[0]
            if git.rebase_in_progress(worktree):
                git.abort_rebase(worktree)
            # Repo caches the current branch; during a stopped rebase it cached
            # detached HEAD, which is stale after abort restores the ticket branch.
            work_repo = Repo(worktree, work_repo.config)
        finally:
            try:
                status_after = work_repo.find(action.id).task.frontmatter.status
            except Exception:  # noqa: BLE001 - preserve the session outcome
                status_after = old_status
            _record_usage(
                project,
                {
                    "ticket": str(action.id),
                    "mode": "rebase",
                    "actor": actor(),
                    "started": started.isoformat().replace("+00:00", "Z"),
                    "seconds": round(time.monotonic() - elapsed_start, 3),
                    "status_before": "review",
                    "status_after": status_after,
                },
            )
        if failure is not None:
            return _fail_review(
                work_repo,
                action,
                "Review failed (integration): rebasing onto `main` conflicts in "
                f"{listed}; the rebase session failed: {failure}",
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
    if changed := git.changed_files(worktree, main_branch, work_repo.config.protected_paths):
        listed = ", ".join(f"`{path}`" for path in changed)
        return _fail_review(
            work_repo,
            action,
            "Review failed (work): the branch changes protected files: "
            f"{listed}. Restore them from `{main_branch}`.",
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
        main_text = run_git(worktree, "show", f"{main_branch}:{relative}")
    except ChittyError:
        return str(relative)
    main = tomllib.loads(main_text).get("tool", {}).get("chitty")
    return str(relative) if current != main else None


def _main_config_path(worktree: Path, main_branch: str) -> str | None:
    """Return the Chitty config path recorded in the integration tree."""
    try:
        run_git(worktree, "show", f"{main_branch}:{CONFIG_NAME}")
    except ChittyError:
        pass
    else:
        return CONFIG_NAME

    try:
        text = run_git(worktree, "show", f"{main_branch}:{PYPROJECT_NAME}")
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
        run_git(main_root, "worktree", "add", str(destination), branch)
    elif action.mode == "review":
        raise ChittyError(f"review ticket {action.id} has no branch {branch}")
    else:
        run_git(main_root, "worktree", "add", "-b", branch, str(destination), main_branch)
    return destination


def _land(main_repo: Repo, worktree: Path, action: NextAction, setup: str, check: str) -> bool:
    """Serialize landing operations that mutate the shared main branch."""
    with locks.landing_lock(main_repo.root):
        try:
            return _land_locked(main_repo, worktree, action, setup, check)
        except LandingCheckFailed:
            raise
        except ChittyError as exc:
            raise ChittyError(
                f"{exc}\nResolve the landing problem in {worktree} "
                "or the main checkout before retrying."
            ) from exc


def _land_locked(
    main_repo: Repo, worktree: Path, action: NextAction, setup: str, check: str
) -> bool:
    """Land a completed ticket and remove its linked worktree."""
    main_root = main_repo.root
    branch = str(action.id).lower()
    # A prior run or a reviewer may already have removed this ticket entirely.
    if not git.has_local_branch(main_root, branch) and not worktree.exists():
        return True
    status = Repo.open(main_root).find(action.id).task.frontmatter.status
    if status != "done":
        print(f"not landing {action.id}: it is {status}", file=sys.stderr)
        return False
    main_branch = main_repo.config.main_branch
    if git.current_branch(main_root) != main_branch:
        raise ChittyError(f"the main checkout must be on branch {main_branch} to land a ticket")
    with locks.main_checkout_lock(main_root):
        git.require_clean(main_root)
    # A session may have landed its own ticket before returning.
    if not worktree.exists():
        return True
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
    quick_attempts = 0
    for attempt in range(LANDING_ATTEMPTS):
        try:
            conflicts = git.rebase_onto(worktree, main_branch)
        except KeyboardInterrupt:
            if git.rebase_in_progress(worktree):
                git.abort_rebase(worktree)
            raise RunInterrupted("rebase") from None
        if conflicts:
            git.abort_rebase(worktree)
            listed = ", ".join(f"`{path}`" for path in conflicts)
            raise ChittyError(
                f"cannot land {action.id}; rebasing onto `{main_branch}` conflicts in {listed}"
            )
        git.add_task_trailers(worktree, main_branch, branch, action.id)
        if changed := _changed_config(worktree, main_branch):
            raise ChittyError(
                f"cannot land {action.id}; the merged branch changes `{changed}`; "
                "only `chitty init` on the main checkout may change it"
            )
        if changed := git.changed_files(worktree, main_branch, main_repo.config.protected_paths):
            listed = ", ".join(f"`{path}`" for path in changed)
            raise ChittyError(
                f"cannot land {action.id}; the branch changes protected files: {listed}"
            )
        _setup(setup, worktree, main_repo.config.command_timeout)
        _landing_check(check, worktree, main_repo.config.command_timeout)
        try:
            with locks.main_checkout_lock(main_root):
                git.require_clean(main_root)
                git.fast_forward(main_root, branch)
        except ChittyError:
            if not git.is_ancestor(main_root, main_branch, branch):
                while quick_attempts < QUICK_LANDING_ATTEMPTS:
                    base = git.merge_base(main_root, branch, main_branch)
                    paths = [str(path) for path in git.changed_paths(main_root, base, main_branch)]
                    if not _only_ticket_paths(paths, list(main_repo.config.contexts)):
                        break
                    quick_attempts += 1
                    try:
                        conflicts = git.rebase_onto(worktree, main_branch)
                    except KeyboardInterrupt:
                        if git.rebase_in_progress(worktree):
                            git.abort_rebase(worktree)
                        raise RunInterrupted("rebase") from None
                    if conflicts:
                        git.abort_rebase(worktree)
                        listed = ", ".join(f"`{path}`" for path in conflicts)
                        raise ChittyError(
                            f"cannot land {action.id}; rebasing onto `{main_branch}` "
                            f"conflicts in {listed}"
                        )
                    try:
                        with locks.main_checkout_lock(main_root):
                            git.require_clean(main_root)
                            git.fast_forward(main_root, branch)
                    except ChittyError:
                        if not git.is_ancestor(main_root, main_branch, branch):
                            continue
                        raise
                    break
                else:
                    base = git.merge_base(main_root, branch, main_branch)
                    paths = [str(path) for path in git.changed_paths(main_root, base, main_branch)]
                    if not _only_ticket_paths(paths, list(main_repo.config.contexts)):
                        if attempt + 1 < LANDING_ATTEMPTS:
                            continue
                        raise ChittyError(
                            f"main moved during each of the {LANDING_ATTEMPTS} landing attempts"
                        ) from None
                    raise ChittyError(
                        f"main moved during each of the {QUICK_LANDING_ATTEMPTS} "
                        "quick landing attempts"
                    ) from None
                if git.is_ancestor(main_root, main_branch, branch):
                    break
                if quick_attempts < QUICK_LANDING_ATTEMPTS and attempt + 1 < LANDING_ATTEMPTS:
                    continue
                if quick_attempts == QUICK_LANDING_ATTEMPTS:
                    raise ChittyError(
                        f"main moved during each of the {QUICK_LANDING_ATTEMPTS} "
                        "quick landing attempts"
                    ) from None
                if attempt + 1 < LANDING_ATTEMPTS:
                    continue
                raise ChittyError(
                    f"main moved during each of the {LANDING_ATTEMPTS} landing attempts"
                ) from None
            raise
        break
    git.remove_worktree(main_root, worktree)
    git.delete_branch(main_root, branch)
    return True


def _landing_check(command: str, worktree: Path, timeout: int) -> None:
    """Run landing validation without changing the ticket on failure."""
    try:
        returncode = run_logged("landing check", command, worktree, timeout)
    except FileNotFoundError:
        raise ChittyError(f"landing check command not found: {command}") from None
    except KeyboardInterrupt:
        raise RunInterrupted("check") from None
    if returncode:
        raise LandingCheckFailed(
            f"landing check exited with status {returncode}; output in `.chitty/check.log`"
        )


def _setup(command: str, worktree: Path, timeout: int) -> None:
    try:
        returncode = run_logged("setup", command, worktree, timeout)
    except FileNotFoundError:
        raise ChittyError(f"setup command not found: {command}") from None
    except KeyboardInterrupt:
        raise RunInterrupted("setup") from None
    if returncode:
        raise ChittyError(f"setup exited with status {returncode}; output in `.chitty/check.log`")


def _runner_error_note(phase: str, error: str, worktree: Path) -> str:
    """Put the first error line in the heading and any remaining output in a fence."""
    lines = error.splitlines() or [""]
    note = f"Runner error ({phase}): {lines[0]}\n\nWorktree: `{worktree}`"
    if any(line.strip() for line in lines[1:]):
        note += "\n\nError output:\n\n" + code_block("\n".join(lines[1:]))
    return note


def _record_ticket_error(
    branch_repo: Repo, action: NextAction, phase: str, error: ChittyError
) -> RunResult:
    """Persist a recoverable runner failure on the ticket branch."""
    worktree = branch_repo.root
    if not worktree.exists():
        raise ChittyError(
            f"cannot record runner error for {action.id}: worktree {worktree} is gone; "
            f"original error: {error}"
        )
    old_status = branch_repo.find(action.id).task.frontmatter.status
    note = _runner_error_note(phase, str(error), worktree)
    try:
        change = branch_repo.edit(
            action.id,
            Edit(
                status="error",
                note=note,
                skip_verdicts=True,
                skip_current_version=True,
            ),
        )
    except ChittyError as handoff_error:
        raise ChittyError(
            f"cannot record runner error for {action.id}: {handoff_error}; original error: {error}"
        ) from handoff_error
    return RunResult(action, old_status, change.task.task.frontmatter.status)


def display_path(path: Path, main_root: Path) -> str:
    return str(path.relative_to(main_root)) if path.is_relative_to(main_root) else str(path)


def _run_check(
    branch_repo: Repo,
    main_root: Path,
    action: NextAction,
    command: str,
    selected_status: str,
    timeout: int,
) -> RunResult | None:
    """Validate the prepared worktree before spending an agent or review session."""
    print(f"{action.id}: running check in {display_path(branch_repo.root, main_root)}...", file=sys.stderr)
    try:
        returncode = run_logged("check", command, branch_repo.root, timeout)
    except CommandTimedOut as error:
        return _handle_check_failure(
            branch_repo, action, str(error), exited=True, selected_status=selected_status
        )
    except FileNotFoundError:
        output = f"check command not found: {command}"
        return _handle_check_failure(
            branch_repo, action, output, exited=False, selected_status=selected_status
        )
    except KeyboardInterrupt:
        raise RunInterrupted("check") from None
    if returncode == 0:
        return None
    detail = f"check exited with status {returncode}; output in `.chitty/check.log`"
    if (
        action.mode == "work"
        and selected_status == "todo"
        and not _branch_has_work(branch_repo.root, branch_repo.config.main_branch)
    ):
        detail += "; the branch has no work yet, so `main` fails this check"
    return _handle_check_failure(
        branch_repo, action, detail, exited=True, selected_status=selected_status
    )


def _handle_check_failure(
    branch_repo: Repo,
    action: NextAction,
    detail: str,
    *,
    exited: bool,
    selected_status: str,
) -> RunResult | None:
    """Start the agent on an unfinished work ticket whose check exited non-zero."""
    if (
        action.mode == "work"
        and exited
        and (
            selected_status in {"doing", "error"}
            or (
                selected_status == "todo"
                and _branch_has_work(branch_repo.root, branch_repo.config.main_branch)
            )
        )
    ):
        branch_repo.edit(
            action.id,
            Edit(note=f"Check failed before this session: {detail}", skip_verdicts=True),
        )
        return None
    return _record_ticket_error(branch_repo, action, "check", ChittyError(detail))
