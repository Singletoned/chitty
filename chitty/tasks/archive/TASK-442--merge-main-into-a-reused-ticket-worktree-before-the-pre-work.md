---
title: Merge main into a reused ticket worktree before the pre-work check
status: backlog
created: 2026-11-19
---

## Description

In circuitry, `chitty run` reused `.worktrees/circuit-96` (branch at an old `main` commit, no ticket work) and ran the configured `check` before merging `main`. A test fix already on `main` (`b26a184`) was therefore missing, and CIRCUIT-96 went to error twice with the same failure. Expected: merge (or fast-forward) `main` into a reused worktree branch before running setup and checks, as already happens before landing.

## Notes

Suggestion origin: circuitry

Archived as covered by `TASK-370` (rebase the ticket branch onto `main` before every work session).

## History

- 2026-11-19T20:55:14Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:15Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:07Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:10Z sunny-white-dormouse backlog → archived
