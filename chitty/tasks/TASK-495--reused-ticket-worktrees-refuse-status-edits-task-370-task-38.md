---
title: "Reused ticket worktrees refuse status edits: TASK-370/TASK-384 now block real runs"
status: backlog
created: 2026-11-21
---

## Description

Evidence from echonomicon, 2026-11-19 (chitty 0.6.1). Worktrees `task-156`, `157`, `159`, `160`, `161` and `163` were created this morning. Later, `chitty run` claimed each ticket `todo → doing` on `main` and then reused the old worktree unchanged (`_worktree` in `src/chitty/run.py` returns an existing worktree as is). The ticket copy on `main` was then newer than the branch copy, so every `chitty edit` from the worktree failed with "latest committed version is on branch main; run Chitty in worktree <main checkout>" (`_require_current_version`, `store.py`). Workers could not set `review`. Some sent tickets to `planning` asking for the branch association to be fixed (TASK-163), some stayed in `error`, and the repair loop exited 1. Branches now differ from `main` both ways (for example `task-157`: 10 own commits, 9 behind). The planned fixes are TASK-384 (claim on the branch) and TASK-370 (rebase onto `main` before each work session). Until they land, a minimal stopgap would help: in work mode, before starting the agent, refuse or rebase a reused worktree whose branch lacks `main`s latest commit for that ticket file.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-21T07:57:58Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:59Z nimble-umber-gannet: changed notes
