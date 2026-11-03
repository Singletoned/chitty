---
title: Write session usage from the Pi extension
status: todo
priority: high
depends_on:
  - TASK-129
  - TASK-134
parent: TASK-106
created: 2026-11-03
---

## Description

Extension half of `TASK-127`, which holds the design under "How it gets there": on `session_shutdown`, if `CHITTY_USAGE_FILE` is set, sum all assistant messages by provider and model, and replace this session's entry in `{"sessions": {"<session id>": [<model entries>]}}`, writing atomically with a rename. Entries are `{"provider", "model", "input", "output", "cacheRead", "cacheWrite", "cost"}`, with `cost` from `usage.cost.total`. The file is written only by this code and read only by `chitty run`.

File: `src/chitty/integrations/pi/chitty.ts`. Export a pure summing function for the Node tests. The handler catches its own errors and reports them with `ctx.ui.notify`.

Out of scope: anything in `chitty run`, and the log itself.

## Acceptance Criteria

- [ ] Node tests show the extension summing every field by provider and model, tolerating a message with no usage, counting abandoned branches, keeping another session ID in the file, replacing its own on a second shutdown, and writing nothing when `CHITTY_USAGE_FILE` is unset
- [ ] `__version__` is bumped above `main`'s

## Notes

Waits for `TASK-134`, so this extension change reaches the machine by itself.

## History

- 2026-11-03T20:46:19Z lively-panda → todo
- 2026-11-03T21:21:53Z lively-panda: changed dependencies, notes
