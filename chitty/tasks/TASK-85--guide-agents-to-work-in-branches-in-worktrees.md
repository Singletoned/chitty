---
title: Guide agents to work in branches in `.worktrees/`
status: todo
priority: high
depends_on:
  - TASK-84
created: 2026-11-01
---

## Description

Agents working directly on `main` collide with each other and with the human. The managed guide should say that work probably belongs in a branch in a worktree, unless the agent's other instructions say otherwise, and that without conflicting instructions worktrees go in `.worktrees/` at the repository root. `chitty init` adds `.worktrees/` to `.gitignore`. Undecided (human, 2026-11-01): who merges back into `main`, and whether to use `git flow` with release branches; settle that before this lands.

## Acceptance Criteria

- [ ] The managed guide gives the worktree rule and the `.worktrees/` default, deferring to the agent's own instructions
- [ ] `chitty init` adds `.worktrees/` to `.gitignore` when missing
- [ ] The guide requires `autocommit = true` (or committing after every Chitty write) when working in a worktree, so other branches can see task state (TASK-84)

## Notes

Merge policy decided (2026-11-01): the reviewer who passes branch work merges it into `main`; already in the guide via TASK-86.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
