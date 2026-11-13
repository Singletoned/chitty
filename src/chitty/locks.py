"""Per-ticket run locks, so concurrent `chitty run` sessions take different tickets.

A lock is an exclusive `flock` on `<git common dir>/chitty/run/<ID>.lock`, so
every worktree of a clone sees the same locks and nothing is committed. The
kernel releases a `flock` when its process exits, however it exits, so a lock
is never stale. Locks are machine-local: Chitty runs on one machine today.
"""

import fcntl
import json
import os
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

from chitty.config import git_common_dir
from chitty.errors import ChittyError

LOCK_SUFFIX = ".lock"
LANDING_LOCK = "landing.lock"


class TicketLocked(ChittyError):
    """Another process holds this ticket's run lock."""


def _directory(root: Path) -> Path | None:
    common = git_common_dir(root)
    return None if common is None else common / "chitty" / "run"


@contextmanager
def run_lock(
    root: Path,
    task_id: str,
    *,
    actor: str,
    mode: Literal["work", "review", "errors"],
) -> Generator[None]:
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
            content = path.read_text().strip() or "unknown"
            try:
                parsed: object = json.loads(content)
                record = cast(dict[str, Any], parsed) if isinstance(parsed, dict) else None
                process = record.get("pid", content) if record is not None else content
            except json.JSONDecodeError:
                process = content
            raise TicketLocked(f"{task_id} is being run by process {process}") from None
        record = {
            "pid": os.getpid(),
            "actor": actor,
            "mode": mode,
            "started": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        os.ftruncate(descriptor, 0)
        os.write(descriptor, (json.dumps(record) + "\n").encode())
        yield
    finally:
        os.close(descriptor)


@contextmanager
def landing_lock(root: Path) -> Generator[None]:
    """Serialize Git mutations that land different tickets onto the same branch."""
    directory = _directory(root)
    if directory is None:
        raise ChittyError(f"{root} is not in a Git repository")
    directory.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(directory / LANDING_LOCK, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
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


def holder(root: Path, task_id: str) -> dict[str, Any] | None:
    """Return the held lock record, including for a lock held by this process.

    The record gains `you`: true when its actor is this session's `CHITTY_ACTOR`,
    so a worker does not mistake its own parent's lock for a rival's.
    """
    record = _record(root, task_id)
    if record is None:
        return None
    return {**record, "you": _is_you(record)}


def _is_you(record: dict[str, Any]) -> bool:
    # Read the variable directly: `actor()` raises when no identity is set, and
    # a record without an actor (a bare pid) is never this session's.
    session = os.environ.get("CHITTY_ACTOR")
    return bool(session) and record.get("actor") == session


def _record(root: Path, task_id: str) -> dict[str, Any] | None:
    if not is_locked(root, task_id):
        return None
    directory = _directory(root)
    assert directory is not None
    path = directory / f"{task_id}{LOCK_SUFFIX}"
    try:
        content = path.read_text().strip()
    except FileNotFoundError:
        return None
    if not content:
        return {"pid": "unknown"}
    try:
        parsed: object = json.loads(content)
    except json.JSONDecodeError:
        return {"pid": content}
    if isinstance(parsed, dict):
        return cast(dict[str, Any], parsed)
    return {"pid": content}


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
