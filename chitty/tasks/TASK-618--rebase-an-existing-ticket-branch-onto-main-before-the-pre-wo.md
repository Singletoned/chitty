---
title: Rebase an existing ticket branch onto main before the pre-work check
status: backlog
created: 2026-11-23
---

## Description

In taidy (2026-11-22), TASK-4 went `todo` → `doing` → `error` in 2 seconds after its dependency TASK-21 landed on `main`. The runner ran `make check` on the existing `task-4` branch, which predated TASK-21, so the check still failed on problems `main` had already fixed. A manual `git rebase main` (ticket-file conflicts only, because the runner also writes notes for the ticket on `main`) made the check pass. Suggestion: before the pre-work check on an existing branch, rebase it onto `main` (or run the check on `main` and only blame the branch for new failures), and resolve conflicts that touch only the ticket file automatically, since Chitty owns that file.

## Notes

Suggestion origin: taidy

## History

- 2026-11-23T10:24:15Z witty-russet-gannet → backlog
- 2026-11-23T10:24:16Z witty-russet-gannet: changed notes
