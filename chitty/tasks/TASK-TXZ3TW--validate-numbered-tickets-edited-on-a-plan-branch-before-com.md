---
title: Validate numbered tickets edited on a `plan/` branch before committing them
status: backlog
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

Seen 2026-11-26: `chitty edit TASK-660 -s cold-read --title ...` on branch `plan/round-5` committed and printed `warning: skipped: read from main` for the ticket's own file. `Repo._commit` (`src/chitty/store.py`) validates written task files with `check.fix`, and `fix` (`src/chitty/check.py`) skips any file whose `repo.source_of(task_id)` is not the working tree. On a plan branch a numbered ticket's source is `main`, so its edits are committed without the safe repairs or the error check that block a broken write elsewhere. Suggest: validate the files a write just made regardless of source, for example by passing them to `fix` as wanted paths that are never skipped. TASK-XZS6RV runs `check` for moves into `cold-read` and `todo` for the same reason.

## History

- 2026-11-26T17:47:42Z calm-ochre-quail → backlog
