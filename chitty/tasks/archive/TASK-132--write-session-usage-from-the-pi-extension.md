---
title: Write session usage from the Pi extension
status: done
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

- [x] Node tests show the extension summing every field by provider and model, tolerating a message with no usage, counting abandoned branches, keeping another session ID in the file, replacing its own on a second shutdown, and writing nothing when `CHITTY_USAGE_FILE` is unset
- [x] `__version__` is bumped above `main`'s

## Plan

1. Add focused Node coverage for shutdown usage aggregation and persistence states from the ticket.
2. Export a pure aggregator and add the shutdown handler that conditionally reads, replaces this session entry, and atomically rewrites the JSON file.
3. Bump the package version, run the Node tests and `make check`, then tick criteria only after their stated verification.

## Notes

Waits for `TASK-134`, so this extension change reaches the machine by itself.

Cold-read attempt: the required fresh `explorer` subagent was unavailable twice (it reported already processing). I will retry before review and record every finding or explicitly record that none were found. No implementation has started.

Cold-read outcome: no code findings recorded because the required fresh `explorer` subagent remained unavailable after three attempts, each returning `Agent is already processing`. This is a harness availability failure, not a code decision; a separate reviewer must perform the independent review.

Verified before ticking: npm test passed all 22 Node tests, including aggregation, missing usage, abandoned-branch entries via getEntries(), retention of another session, replacement on second shutdown, and no write with CHITTY_USAGE_FILE unset. make check also passed; the version is 0.1.24, above main version 0.1.23.

Per human direction, skip the cold read: it belongs to planning rather than workers and has been removed from the worker instructions on main. Do not retry it.

Re-checked every criterion before review: npm test passed all 22 Node tests and make check passed. Independent review is now required.

Reviewed: criterion 1 verified by independent inspection and passing Node tests: aggregates every usage field by provider/model, retains no-usage assistant messages, uses all session entries, atomically preserves other sessions and replaces this session, and skips an unset file. Criterion 2 verified: 0.1.24 is above main 0.1.23. Verification: npm test; make check (219 Python tests, Ruff, Pyright).

## History

- 2026-11-03T20:46:19Z lively-panda → todo
- 2026-11-03T21:21:53Z lively-panda: changed dependencies, notes
- 2026-11-04T09:12:08Z jolly-crane: changed notes; wrote the plan
- 2026-11-04T09:12:08Z jolly-crane todo → doing
- 2026-11-04T09:16:23Z jolly-crane: changed notes
- 2026-11-04T09:21:42Z jolly-crane: changed notes; ticked acceptance criteria
- 2026-11-04T09:22:35Z jolly-crane: changed notes
- 2026-11-04T09:23:51Z jolly-crane: changed notes
- 2026-11-04T09:23:51Z jolly-crane doing → review
- 2026-11-04T09:29:41Z lively-stoat: changed notes
- 2026-11-04T09:29:41Z lively-stoat review → done
- 2026-11-05T14:44:53Z vivid-wren done → archived
