---
title: Guide agents to work in branches in `.worktrees/`
status: done
priority: high
depends_on:
  - TASK-84
parent: TASK-58
created: 2026-11-01
---

## Description

Agents working directly on `main` collide with each other and with the human. The managed guide should say that work probably belongs in a branch in a worktree, unless the agent's other instructions say otherwise, and that without conflicting instructions worktrees go in `.worktrees/` at the repository root. `chitty init` adds `.worktrees/` to `.gitignore`. Undecided (human, 2026-11-01): who merges back into `main`, and whether to use `git flow` with release branches; settle that before this lands.

## Acceptance Criteria

- [x] The managed guide gives the worktree rule and the `.worktrees/` default, deferring to the agent's own instructions
- [x] `chitty init` adds `.worktrees/` to `.gitignore` when missing
- [x] The guide requires `autocommit = true` (or committing after every Chitty write) when working in a worktree, so other branches can see task state (TASK-84)

## Plan

Update the managed guide and `init` setup so agents are directed to use repository-root `.worktrees/` worktrees unless superseded by their own instructions. Require worktree task-state visibility through `autocommit = true` or commits after every Chitty write. Add focused regression tests, run the targeted tests and `make check`, then submit the ticket for independent review.

## Notes

Merge policy decided (2026-11-01): the reviewer who passes branch work merges it into `main`; already in the guide via TASK-86.

Blocked by `TASK-84`: cross-branch state visibility must be completed before the guide can require worktrees and autocommit.

Unblocked (2026-11-01): TASK-84 passed review, so other branches' task state is visible.

Implemented managed-guide worktree and task-state visibility rules, `.gitignore` setup, and regression coverage. Verified with `chitty fix`, `chitty check`, and `make check`; existing unrelated Markdown-delimiter warnings remain.

Reviewed: Ed Singleton implemented the managed guide and init setup in 0e29596. Independently verified the focused init regression, `chitty check`, and `make check`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
- 2026-11-05T14:44:48Z vivid-wren done → archived
