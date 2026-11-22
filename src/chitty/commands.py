import os
import re
import shlex
import signal
import subprocess
import time
from pathlib import Path

from chitty.errors import ChittyError

AGENT_KILL_GRACE_SECONDS = 2
RUN_LOG = Path(".chitty/check.log")
RUN_LOG_EXCLUDE = f"/{RUN_LOG.parent}/"


def command_environment() -> dict[str, str]:
    """Copy the environment without an inherited usage file."""
    environment = os.environ.copy()
    # An inherited value would make an agent write a file `chitty run` no longer reads.
    environment.pop("CHITTY_USAGE_FILE", None)
    return environment


def terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    descendants = process_descendants(process.pid)
    for pid in [*descendants, process.pid]:
        signal_process(pid, signal.SIGTERM)
    grace_deadline = time.monotonic() + AGENT_KILL_GRACE_SECONDS
    while time.monotonic() < grace_deadline:
        if not running_processes([*descendants, process.pid]):
            break
        time.sleep(min(0.05, grace_deadline - time.monotonic()))
    for pid in running_processes([*descendants, process.pid]):
        signal_process(pid, signal.SIGKILL)
    process.wait()


def process_descendants(parent: int) -> list[int]:
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


def running_processes(pids: list[int]) -> list[int]:
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


def signal_process(pid: int, sig: signal.Signals) -> None:
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass


def with_exclude_line(text: str | None) -> str:
    """Return exclude-file text with exactly one run-log exclusion."""
    lines = [] if text is None or text == "" else text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if RUN_LOG_EXCLUDE not in lines:
        lines.append(RUN_LOG_EXCLUDE)
    else:
        first = lines.index(RUN_LOG_EXCLUDE)
        lines = [
            line for index, line in enumerate(lines) if line != RUN_LOG_EXCLUDE or index == first
        ]
    return "\n".join(lines) + "\n"


def ignore_run_log(worktree: Path) -> None:
    """Ignore the run log using Git's shared exclude file."""
    exclude = Path(run_git(worktree, "rev-parse", "--git-path", "info/exclude").strip())
    if not exclude.is_absolute():
        exclude = worktree / exclude
    existing = exclude.read_text() if exclude.exists() else None
    updated = with_exclude_line(existing)
    if updated != existing:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(updated)


class CommandTimedOut(ChittyError):
    """A runner command exceeded its deadline."""


def run_logged(phase: str, command: str, worktree: Path, timeout: int) -> int:
    """Run a command with combined output in the worktree's last-run log."""
    argv = shlex.split(command)
    ignore_run_log(worktree)
    log_path = worktree / RUN_LOG
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Binary mode: the command's output may be any bytes, and checking its last
    # byte must not decode it.
    with log_path.open("w+b") as log:
        log.write(f"# chitty {phase}: {command}\n".encode())
        log.flush()
        timed_out = False
        with subprocess.Popen(
            argv,
            cwd=worktree,
            stdin=subprocess.DEVNULL,
            env=command_environment(),
            stdout=log,
            stderr=subprocess.STDOUT,
        ) as process:
            try:
                try:
                    process.wait(timeout=timeout or None)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    terminate_process_tree(process)
            except BaseException:
                process.kill()
                raise
        log.seek(0, os.SEEK_END)
        end = log.tell()
        log.seek(end - 1 if end else 0)
        if log.read(1) != b"\n":
            log.seek(0, os.SEEK_END)
            log.write(b"\n")
        if timed_out:
            log.write(f"# timed out after {timeout} seconds\n".encode())
            raise CommandTimedOut(
                f"{phase} timed out after {timeout} seconds; output in `{RUN_LOG}`"
            )
        log.write(f"# exit {process.returncode}\n".encode())
    return process.returncode


def code_block(text: str) -> str:
    """Fence command output so a note cannot read it as Markdown structure."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise ChittyError(completed.stderr.strip() or f"git {' '.join(arguments)} failed")
    return completed.stdout
