---
title: Guide agents to work in branches in `.worktrees/`
status: backlog
depends_on:
  - TASK-84
created: 2026-11-01
---

## Description

Agents working directly on `main` collide with each other and with the human. The managed guide should say that work probably belongs in a branch in a worktree, unless the agent's other instructions say otherwise, and that without conflicting instructions worktrees go in `.worktrees/` at the repository root. `chitty init` adds `.worktrees/` to `.gitignore`. Undecided (human, 2026-11-01): who merges back into `main`, and whether to use `git flow` with release branches; settle that before this lands.

## Acceptance Criteria

- [ ] The managed guide gives the worktree rule and the `.worktrees/` default, deferring to the agent's own instructions
- [ ] `chitty init` adds `.worktrees/` to `.gitignore` when missing
- [ ] The guide says who merges finished work back and when

## History

- 2026-11-01 → backlog
