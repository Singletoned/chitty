---
title: Allow Chitty writes from a ticket worktree
status: doing
priority: high
created: 2026-11-03
---

## Description

A worktree with the same `project` configuration cannot run `chitty edit`: `register_project` treats the main checkout owner as a different repository. This blocks the documented worktree workflow from committing claims and review results. Recognize Git worktrees of the registered repository as the same owner, while preserving the collision guard for unrelated repositories.

## Acceptance Criteria

- [ ] In a Git worktree of the registered repository, `chitty init`, `chitty inbox --pull` and a write that triggers a setup upgrade all succeed, and the registered path stays the main checkout
- [ ] An unrelated repository using the same `project` name is still refused
- [ ] Tests create a real `git worktree` and cover both cases

## Plan

1. Reproduce registration from an actual Git worktree and locate the ownership check.
2. Teach project registration to recognise sibling worktrees by their shared Git common directory while retaining unrelated-path rejection.
3. Add real-worktree tests for successful setup and upgrade writes plus collision refusal.
4. Run the focused tests and `make check`, then tick criteria and record the handoff.

## Notes

Suggestion origin: chitty

Narrowed on 2026-11-03: a plain `chitty edit` works from a worktree. `register_project` only runs from `init_repo` and `inbox.pull`, so what fails is `chitty init` (reproduced in the `task-105` worktree), `chitty inbox --pull`, which the guide says to run first, and writes when setup is stale. A version bump therefore breaks writes in worktrees that have not yet got the bump. Prerequisite for the `TASK-109` pilot.

## History

- 2026-11-03T09:38:44Z mellow-marten → backlog
- 2026-11-03T09:38:45Z mellow-marten: changed notes
- 2026-11-03T10:41:00Z lively-panda: changed priority, acceptance criteria, notes
- 2026-11-03T10:41:00Z lively-panda backlog → todo
- 2026-11-03T10:42:41Z ivory-quail: wrote the plan
- 2026-11-03T10:42:41Z ivory-quail todo → doing
