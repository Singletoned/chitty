---
title: Keep the output of the last check run in a gitignored log
status: backlog
created: 2026-11-16
---

## Description

Runner check output is written into ticket notes (`Check failed before this session` in `src/chitty/run.py`), which bloats tickets. Write the full output of the last configured check run in a worktree to a gitignored file inside that worktree, so the worker can read it without leaving the worktree, and put only a short summary and the file path in the note. `TASK-338` uses the same file for its tests-fail-without-the-change run. Planning decides the path and how `chitty init` adds it to `.gitignore`.

## History

- 2026-11-16T10:00:06Z intrepid-coral-raven → backlog
