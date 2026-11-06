---
title: Stop concurrent `chitty run` sessions taking the same ticket
status: backlog
priority: high
parent: TASK-106
created: 2026-11-06
---

## Description

The human wants several `chitty run --mode review` loops, and in time several workers, running at once in this repository. Today two loops started together choose the same ticket: `next_action` in `src/chitty/store.py` picks the first eligible ticket, and nothing marks it as taken until the agent commits a status change, which for a review is at the very end. `README.md` currently allows only one worker and one reviewer.

Add a per-ticket run lock, held by `chitty run` from just after it chooses a ticket until it returns. The lock is a file at `<git common dir>/chitty/run/<ID>.lock` of the main checkout (`git rev-parse --git-common-dir`), so every worktree of the clone sees the same locks and nothing is committed. Create it with `os.open(..., O_CREAT | O_EXCL | O_WRONLY)` and write the holder's PID. Remove it in a `finally` in `run` in `src/chitty/run.py`, including on `RunInterrupted` and any other exception. A lock whose PID is not running (`os.kill(pid, 0)` raises `ProcessLookupError`) is stale: whoever finds it deletes it and carries on. A committed note or field was considered and rejected: a killed run would leave it behind for a person to clear, and every claim and release would be a commit on a branch other sessions read.

The decision: a lock is machine-local, because Chitty runs on one machine today (the human, 2026-11-06). Locks on other machines are out of scope.

`next_action` skips a ticket with a live lock, in both modes and with no `--mode`, so `chitty next` agrees with `chitty run`. `run` takes the lock after `next_action` returns, and if another process created it first (`FileExistsError`) it asks `next_action` again, which now skips that ticket; a bounded number of attempts is enough, because each lost race removes a candidate. When nothing unlocked remains it raises `NoNextTicket` as today, so an idle loop still exits 3. `chitty run --ticket ID` refuses a ticket with a live lock with a `ChittyError` naming the PID. Take the lock before `_worktree`, `_prepare_review` and setup, and before claiming a `todo` ticket, so two runs never touch one worktree.

Out of scope: collisions in the main checkout itself, which `README.md` already says fail loudly (Git locks during setup, inbox pulls and review merges), and showing locks in `chitty list`, which `TASK-72` can add.

## Acceptance Criteria

- [ ] Tests show two `chitty run --mode review` processes started together, with two review tickets and fake agents that wait, each reviewing a different ticket, and a third exiting 3
- [ ] Tests show a stale lock (a PID that is not running) being taken over, `chitty next` skipping a live lock, `--ticket` refusing one, and the lock removed after a run that succeeds, fails and is interrupted
- [ ] `README.md` and `PLAN.md` say any number of workers and reviewers may run at once and describe the lock

## History

- 2026-11-06T09:26:15Z youthful-toad → backlog
