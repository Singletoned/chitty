"""Per-ticket run locks, so concurrent `chitty run` sessions take different tickets.

A lock is an exclusive `flock` on `<git common dir>/chitty/run/<ID>.lock`, so
every worktree of a clone sees the same locks and nothing is committed. The
kernel releases a `flock` when its process exits, however it exits, so a lock
is never stale. Locks are machine-local: Chitty runs on one machine today.
"""

import fcntl
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from chitty.config import git_common_dir
from chitty.errors import ChittyError

LOCK_SUFFIX = ".lock"


class TicketLocked(ChittyError):
    """Another process holds this ticket's run lock."""


def _directory(root: Path) -> Path | None:
    common = git_common_dir(root)
    return None if common is None else common / "chitty" / "run"


@contextmanager
def run_lock(root: Path, task_id: str) -> Generator[None]:
    """Hold `task_id`'s run lock for the block, or raise `TicketLocked`."""
    directory = _directory(root)
    if directory is None:
        raise ChittyError(f"{root} is not in a Git repository")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{task_id}{LOCK_SUFFIX}"
    # `os.open` descriptors are not inherited, so the agent cannot keep the lock.
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            holder = path.read_text().strip() or "unknown"
            raise TicketLocked(f"{task_id} is being run by process {holder}") from None
        # The PID is only for messages; the lock is the `flock` itself.
        os.ftruncate(descriptor, 0)
        os.write(descriptor, f"{os.getpid()}\n".encode())
        yield
    finally:
        os.close(descriptor)


def locked_ids(root: Path) -> set[str]:
    """IDs whose run lock another descriptor holds, including in this process."""
    directory = _directory(root)
    if directory is None or not directory.is_dir():
        return set()
    return {
        path.name.removesuffix(LOCK_SUFFIX)
        for path in directory.glob(f"*{LOCK_SUFFIX}")
        if _held(path)
    }


def is_locked(root: Path, task_id: str) -> bool:
    return task_id in locked_ids(root)


def _held(path: Path) -> bool:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except FileNotFoundError:
        return False
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return True
    finally:
        # Closing also releases the probe's own lock when it got one.
        os.close(descriptor)
    return False
