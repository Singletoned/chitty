---
title: Stop concurrent `chitty run` sessions taking the same ticket
status: done
priority: high
parent: TASK-106
created: 2026-11-06
---

## Description

The human wants several `chitty run --mode review` loops, and in time several workers, running at once in this repository. Today two loops started together choose the same ticket: `next_action` in `src/chitty/store.py` picks the first eligible ticket, and nothing marks it as taken until the agent commits a status change, which for a review is at the very end. `README.md` and `PLAN.md` currently allow only one worker and one reviewer.

Add a per-ticket run lock in a new module `src/chitty/locks.py`, held by `chitty run` from just after it chooses a ticket until `run` returns. The lock is an exclusive, non-blocking `fcntl.flock` (`LOCK_EX | LOCK_NB`) on the file `<git common dir>/chitty/run/<ID>.lock` of the clone (use the existing `_git_common_dir` in `src/chitty/config.py`; create the directory with `parents=True, exist_ok=True`), so every worktree sees the same locks and nothing is committed. The kernel releases a `flock` when its process exits, however it exits, so there is no stale lock to detect or take over, and the file itself is left in place and never deleted. After locking, the holder truncates the file and writes its PID, which is only for messages.

Decisions, so the worker need not make them:
- A committed note or field was rejected: a killed run would leave it for a person to clear, and every claim would be a commit. PID files were rejected after a cold read: taking over a stale one races, and PIDs are reused.
- Locks are machine-local, because Chitty runs on one machine today (the human, 2026-11-06). Other machines are out of scope.
- `locks.py` provides a context manager `run_lock(root, task_id)`, raising `TicketLocked` (a `ChittyError`) if the lock is held, and `is_locked(root, task_id) -> bool`, which tries the same `flock` on a fresh file descriptor and releases it at once, and returns `False` when the file does not exist. A fresh descriptor conflicts even with a lock held by the same process, which the retry below relies on.
- `next_action` calls `is_locked(repo.root, stored.id)` and skips a locked ticket in both modes and with no `--mode`, so `chitty next` and the MCP `next` tool agree with `chitty run`. `ticket_action` (the `--ticket` path) does not skip it; `run` refuses it instead.
- `run` in `src/chitty/run.py` enters `run_lock` immediately after choosing the ticket, before the dirty-path check, `_worktree`, `_prepare_review`, setup and the `todo` claim, and everything after it runs inside the `with`, so every exit releases it. Extract this into a helper: `run` is already over 100 lines. If `run_lock` raises `TicketLocked` for a ticket `next_action` chose, another run took it between the check and the lock: ask `next_action` again, up to a module-level `RUN_LOCK_ATTEMPTS = 10`, then raise the last `TicketLocked`. When nothing unlocked remains `next_action` raises `NoNextTicket` as today, so an idle loop still exits 3. `chitty run --ticket ID` on a locked ticket raises `TicketLocked` naming the PID from the file.
- No version bump: this changes no guide, `chitty.toml` template or inbox registration.

Tests can hold a lock from the test process with `run_lock`, and run two real `chitty run` processes with fake agents on `PATH`, as `tests/test_next.py` does, where each agent waits for a file the test creates, so both sessions overlap. Run every test with stdin closed.

Out of scope: collisions in the main checkout itself, which `README.md` already says fail loudly (Git locks during setup, inbox pulls and review merges), and showing locks in `chitty list`, which `TASK-72` can add later.

## Acceptance Criteria

- [x] Tests show two `chitty run --mode review` processes started together, with two review tickets and fake agents that wait, each reviewing a different ticket, and a third exiting 3
- [x] `README.md` and `PLAN.md` say any number of workers and reviewers may run at once and describe the lock
- [x] Tests show a lock held by another process making `chitty next` skip that ticket and `--ticket` refuse it with its PID, and the lock free again after a run that succeeds, fails and is interrupted

## Plan

1. Tests first: `tests/test_run_lock.py` for `locks.run_lock`/`is_locked` (held by a child process, released on exit), `chitty next` skipping a locked ticket, `--ticket` refusing with the PID, the lock free after success, failure and interrupt, and two real `chitty run --mode review` processes with waiting fake agents reviewing different tickets while a third exits 3.
2. `src/chitty/locks.py`: `flock` on `<git common dir>/chitty/run/<ID>.lock`, `TicketLocked`.
3. `next_action` skips locked tickets; `run` takes the lock right after selection in a helper, retrying up to `RUN_LOCK_ATTEMPTS`.
4. `README.md` and `PLAN.md`.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-06. Fixed: the PID-file design raced on stale takeover, on an empty file before the PID is written, and on PID reuse, so it now uses `fcntl.flock`, which the kernel releases on exit; named the module, the API, what `next_action` calls, the retry bound, the lock directory's creation, that the lock covers the dirty-path check and early returns, the test approach, and no version bump. The size concern is answered by the simpler lock; three criteria.

Owner set to human only so chitty run leaves this ticket to this session; cleared when done.

`next_action` uses `locks.locked_ids(root)`, one `git rev-parse` per call, rather than `is_locked` per ticket as the description says, which would run Git once per candidate; `is_locked` remains and uses it. Renamed `config._git_common_dir` to `git_common_dir` so `locks.py` can import it.

Reviewed: independently inspected the lock implementation, runner/store integration, documentation, and tests. All three acceptance criteria are met. make check passes: 300 Python tests and Node tests.

## Summary

New `src/chitty/locks.py`: `run_lock(root, id)` takes an exclusive non-blocking `flock` on `<git common dir>/chitty/run/<ID>.lock` and writes the PID for messages, raising `TicketLocked`; `locked_ids`/`is_locked` probe with a fresh descriptor. `next_action` skips locked tickets. `run` now chooses and locks in `_lock_ticket` (retrying up to `RUN_LOCK_ATTEMPTS`; `--ticket` refuses a locked one) inside an `ExitStack`, and the rest moved unchanged to `_run_ticket`, so the lock covers the dirty-path check, worktree, rebase, setup, claim and agent. `README.md` and `PLAN.md` now allow any number of workers and reviewers.

Verified: `tests/test_run_lock.py` (three of four failed before wiring the lock in; the kernel-release test needs only `locks.py`): a SIGKILLed holder frees the lock, `chitty next` skips a locked ticket and exits 3 when all are, `--ticket` names the PID, the lock is held during the agent and free after success, failure and interrupt, and two real `chitty run --mode review` processes with waiting agents review different tickets while a third exits 3. `make check` passes (295 tests plus Node). Follow-up: `TASK-72` could show locked tickets in `chitty list`.

## History

- 2026-11-06T09:26:15Z youthful-toad → backlog
- 2026-11-06T09:28:32Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T09:31:14Z youthful-toad backlog → todo
- 2026-11-06T10:00:40Z youthful-toad: changed owner, notes
- 2026-11-06T10:00:44Z youthful-toad: wrote the plan
- 2026-11-06T10:00:44Z youthful-toad todo → doing
- 2026-11-06T10:09:19Z youthful-toad: changed owner, notes, summary; ticked acceptance criteria
- 2026-11-06T10:09:19Z youthful-toad doing → review
- 2026-11-06T10:47:18Z upbeat-crane: changed notes
- 2026-11-06T10:47:18Z upbeat-crane review → done
- 2026-11-06T16:46:12Z jolly-quail done → archived
