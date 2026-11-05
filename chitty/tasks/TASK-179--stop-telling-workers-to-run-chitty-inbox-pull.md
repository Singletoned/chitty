---
title: Stop telling workers to run `chitty inbox --pull`
status: backlog
priority: medium
depends_on:
  - TASK-142
created: 2026-11-05
---

## Description

A worker's first step is `chitty inbox --pull`, from `src/chitty/roles/work.md` line 6 and `src/chitty/guide.md` line 8, which also reaches `AGENTS.md`'s managed block through `chitty init`. `chitty run` already pulls before it starts an agent (`src/chitty/run.py`), so this only spends a call. Seen on 2026-11-05 in a real session on `TASK-142`, where the human said it should not be doing that.

Remove the instruction from both files, leaving `chitty show <ID>` as the first step. `TASK-173` also edits `work.md` and `TASK-143` rewrites `guide.md`, so take whichever lands first into account. Any test that expects the old text changes with it.

## Acceptance Criteria

- [ ] `chitty guide work` and `chitty guide` no longer contain `inbox --pull`, shown by a test, and `chitty inbox --pull` itself still works
- [ ] `__version__` is bumped above `main`'s and `AGENTS.md`'s managed block is refreshed

## History

- 2026-11-05T09:37:44Z mellow-newt → backlog
