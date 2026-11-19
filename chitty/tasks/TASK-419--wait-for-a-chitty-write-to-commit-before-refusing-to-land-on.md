---
title: Wait for a Chitty write to commit before refusing to land on a dirty `main`
status: backlog
created: 2026-11-19
---

## Description

Landing (`_land_locked` in `src/chitty/run.py`) calls `git.require_clean` on the main checkout and refuses when anything is uncommitted. A Chitty write on `main` (with `autocommit`) writes the file and commits it a moment later, so a landing check that falls in between refuses. Seen 2026-11-19 at 10:39 with `TASK-410`: a planning `chitty add TASK-415` (`81e992f8`) had written its file but not yet committed it, landing failed with `working tree is dirty`, and the runner recorded `error` on a ticket whose review had passed. Split from `TASK-418`, which handles `main` moving during the check. Planning needs to decide how long to wait and how to test it without timing (for example an injected wait function).

## History

- 2026-11-19T12:12:29Z quick-ginger-lapwing → backlog
