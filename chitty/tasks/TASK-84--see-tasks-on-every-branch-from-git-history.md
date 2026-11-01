---
title: See tasks on every branch, from Git history
status: review
priority: high
parent: TASK-58
created: 2026-11-01
---

## Description

With work done on branches (TASK-85), each branch has its own copy of `chitty/`. A task set `doing` on one branch is invisible to agents on others, who may start the same task, and two branches that both `chitty add` allocate the same ID.

Decided with the human (2026-11-01): read committed task state from every branch through Git instead of scanning worktree directories. `git for-each-ref` over `refs/heads` and `refs/remotes`, then `git ls-tree` and `git cat-file --batch` on `chitty/`, covers branches without a worktree and, after a fetch, other machines, without checking anything out. The current worktree's uncommitted files are read directly. Other worktrees' uncommitted edits are invisible, so worktree work needs `autocommit = true`; the guide (TASK-85) says so.

A task's current state is its most recent change, not its furthest status: a failed review moves backwards. Until History carries timestamps (TASK-55), use the commit time of the last commit that touched the file on each ref. A merged branch that was never deleted holds an older copy, which this ordering ignores. This revises the 'no cross-branch scanning' principle in `PLAN.md`; ID allocation already reads Git history for `archive = "delete"`.

## Acceptance Criteria

- [x] Reading every branch stays fast on a repository with many branches (one `git cat-file --batch` process, not one command per file); a test covers a task changed only on another branch
- [x] `PLAN.md` records the revised principle and the `autocommit` requirement for worktrees
- [x] `chitty list` and `show` report each task's most recently changed state across local and remote-tracking branches, naming the branch when it is not the current one

## Plan

Trace repository task discovery, `list`/`show`, and Git access; then implement a batched read of committed task files across local and remote-tracking refs that selects each task by its latest file-changing commit, while retaining current-worktree files. Add isolated Git-repository tests for a task changed only on another branch, update `PLAN.md`, run the focused tests and `make check`, and tick each acceptance criterion.

## Notes

Absorbed TASK-59 (claims from `doing/` branches), which is archived. Its open questions are answered here: task state from other branches shows in `list`, `show` and `next`; remote-tracking branches count; reading every branch makes a claim visible without relying on branch names. ID allocation is left to TASK-61 (IDs only on `main`), the earlier design agreed with the human: scanning branches cannot see uncommitted work or unfetched remotes, so it reduces collisions but cannot prevent them.

For whoever resumes this (the claiming agent was stopped before committing code): the Plan predates the removal of the ID-allocation criterion. Skip cross-branch ID allocation; that is TASK-61 (IDs only on `main`).

Implemented and verified cross-branch `list`/`show` reads, batched blob loading, branch attribution, and the revised plan. Acceptance criterion 1 also requires `chitty next`, but that command is TASK-76, which remains backlog and depends on TASK-70, TASK-74 and TASK-75. Resume TASK-84 after TASK-76 is actionable, or split the `next` assertion from this ticket.

Unblocked (2026-11-01): the `chitty next` part of the old criterion 1 moved to TASK-76. The rewritten criterion (now 3) covers `list` and `show` only, which the earlier note says are implemented; verify, tick it, and set `review`.

Verified the cross-branch implementation: `tests/test_store.py` covers state selected from a newer `other` branch; `list` formats the branch and `show` reports `branch:`. Verified the full suite with `make check`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-01 blocked → doing
- 2026-11-01 doing → review
