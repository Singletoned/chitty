---
title: Allow Chitty writes from a ticket worktree
status: backlog
created: 2026-11-03
---

## Description

A worktree with the same `project` configuration cannot run `chitty edit`: `register_project` treats the main checkout owner as a different repository. This blocks the documented worktree workflow from committing claims and review results. Recognize Git worktrees of the registered repository as the same owner, while preserving the collision guard for unrelated repositories.

## Notes

Suggestion origin: chitty

## History

- 2026-11-03T09:38:44Z mellow-marten → backlog
- 2026-11-03T09:38:45Z mellow-marten: changed notes
