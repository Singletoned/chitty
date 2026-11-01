---
title: See tasks in every local worktree
status: backlog
created: 2026-11-01
---

## Description

With work done in branches in worktrees (TASK-85), each worktree has its own copy of `chitty/`. An agent that sets a task `doing` on its branch is invisible to agents on other branches, who may start the same task; two worktrees that both `chitty add` allocate the same ID. `list`, `next` and ID allocation should read every worktree from `git worktree list` (local files only, still no network or branch checkouts): show each task's furthest state and which worktree holds it, and allocate past the highest ID in any of them. This revises the 'no cross-branch scanning' principle in `PLAN.md` for local worktrees only.

## Acceptance Criteria

- [ ] `chitty list` and `chitty next` show a task's state from the worktree where it has progressed furthest, naming that worktree
- [ ] `chitty add` never allocates an ID used in another local worktree
- [ ] `PLAN.md` records the revised principle

## History

- 2026-11-01 → backlog
