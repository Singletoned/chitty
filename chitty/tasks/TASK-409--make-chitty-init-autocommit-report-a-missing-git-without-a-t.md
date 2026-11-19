---
title: Make `chitty init --autocommit` report a missing `git` without a traceback
status: backlog
created: 2026-11-19
---

## Description

Found by a cold read of `TASK-408` (2026-11-19). `chitty init --autocommit` (`init_repo` in `src/chitty/store.py`) runs `git.require_clean` instead of `Repo._prepare_write`. Outside a repository with `git` on `PATH` it exits 1 cleanly and changes no file; with `git` missing from `PATH` it shows a `FileNotFoundError` traceback, also changing no file. It should raise `ChittyError` naming `git` and `PATH`.

## History

- 2026-11-19T09:10:49Z lively-quartz-crane → backlog
