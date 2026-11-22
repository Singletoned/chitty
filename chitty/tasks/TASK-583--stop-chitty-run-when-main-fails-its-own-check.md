---
title: Stop chitty run when main fails its own check
status: todo
created: 2026-11-22
---

## Description

Split from TASK-580 (taidy, 2026-11-22). When the pre-work check fails for a todo ticket whose branch has no work, `main` itself fails the check, so every following ticket in the same `chitty run` will also go to `error`. Decide whether the run should stop instead (and whether the ticket should go back to `todo` rather than `error`). Needs a look at the run loop in `src/chitty/run.py` before planning; TASK-580 adds the message first.

## History

- 2026-11-22T13:19:33Z friendly-jade-stoat → todo
