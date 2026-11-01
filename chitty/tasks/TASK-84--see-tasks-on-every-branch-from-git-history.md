---
title: See tasks on every branch, from Git history
status: doing
priority: high
parent: TASK-58
created: 2026-11-01
---

## Description

With work done on branches (TASK-85), each branch has its own copy of `chitty/`. A task set `doing` on one branch is invisible to agents on others, who may start the same task, and two branches that both `chitty add` allocate the same ID.

Decided with the human (2026-11-01): read committed task state from every branch through Git instead of scanning worktree directories. `git for-each-ref` over `refs/heads` and `refs/remotes`, then `git ls-tree` and `git cat-file --batch` on `chitty/`, covers branches without a worktree and, after a fetch, other machines, without checking anything out. The current worktree's uncommitted files are read directly. Other worktrees' uncommitted edits are invisible, so worktree work needs `autocommit = true`; the guide (TASK-85) says so.

A task's current state is its most recent change, not its furthest status: a failed review moves backwards. Until History carries timestamps (TASK-55), use the commit time of the last commit that touched the file on each ref. A merged branch that was never deleted holds an older copy, which this ordering ignores. This revises the 'no cross-branch scanning' principle in `PLAN.md`; ID allocation already reads Git history for `archive = "delete"`.

## Acceptance Criteria

- [ ] `chitty list`, `show` and `next` report each task's most recently changed state across local and remote-tracking branches, naming the branch when it is not the current one
- [ ] Reading every branch stays fast on a repository with many branches (one `git cat-file --batch` process, not one command per file); a test covers a task changed only on another branch
- [ ] `PLAN.md` records the revised principle and the `autocommit` requirement for worktrees

## Plan

Trace repository task discovery, ID allocation, and the Git wrapper. Design a single batched Git read over branch refs that overlays committed task versions by the commit that last touched each file, while preserving direct reads from the current worktree. Add isolated repository tests for a task that changes only on another branch and for cross-branch ID allocation; then update `PLAN.md` with the branch-state and worktree-autocommit decisions.

## Notes

Absorbed TASK-59 (claims from `doing/` branches), which is archived. Its open questions are answered here: task state from other branches shows in `list`, `show` and `next`; remote-tracking branches count; reading every branch makes a claim visible without relying on branch names. ID allocation is left to TASK-61 (IDs only on `main`), the earlier design agreed with the human: scanning branches cannot see uncommitted work or unfetched remotes, so it reduces collisions but cannot prevent them.

For whoever resumes this (the claiming agent was stopped before committing code): the Plan predates the removal of the ID-allocation criterion. Skip cross-branch ID allocation; that is TASK-61 (IDs only on `main`).

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
