---
title: Run Pi workers and reviewers in their own worktrees
status: todo
priority: high
depends_on:
  - TASK-103
created: 2026-11-02
---

## Description

The human wants to run several workers and reviewers at once in one repo without them overwriting each other or the human's own sessions. Today the Pi prompts say nothing about branches, so most agents commit straight to `main`; one built `TASK-98` on a branch that was never merged while another rebuilt it on `main`, and enabling `autocommit` in `chitty.toml` confused a worker sharing the checkout.

Work mode: claim a ticket, create (or reuse, for a ticket already `doing`) a branch and worktree under `.worktrees/` from `main`, do all code and Chitty writes there, and set `review`. Review mode: review the branch in its worktree; on a pass merge it into `main` and remove the branch and worktree; on a fail set `doing` on the branch. Chitty reads task state across branches, so claims must be committed on the branch before work starts so other agents see them.

## Acceptance Criteria

- [ ] The Pi work prompt tells workers to do each ticket in a branch and worktree under `.worktrees/`, never in the main checkout, and to resume an existing worktree for a `doing` ticket
- [ ] The Pi review prompt tells reviewers to review in the ticket's worktree, merge into `main` on a pass, then remove the branch and worktree
- [ ] A worker's claim (`doing`) is committed on its branch before implementation starts, so a second worker does not pick the same ticket; a test or documented check shows it
- [ ] Node tests cover the prompt wording; `src/chitty/guide.md` matches it and `__version__` is bumped

## Notes

Depends on `TASK-103`: workers in worktrees break the shared venv until each worktree has its own.

## History

- 2026-11-02T11:21:00Z lively-otter → todo
- 2026-11-02T11:21:06Z lively-otter: changed dependencies, notes
