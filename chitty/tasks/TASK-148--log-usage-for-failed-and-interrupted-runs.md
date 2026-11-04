---
title: Log usage for failed and interrupted runs
status: todo
priority: high
depends_on:
  - TASK-127
parent: TASK-106
created: 2026-11-04
---

## Description

Second part of the log designed in `TASK-127`, which already writes a line for a session that ends normally. A session that cost money must not vanish, and dead and unchanged sessions are the expensive ones.

Write the line in a `finally` in `src/chitty/run.py`, covering a non-zero agent exit, Ctrl-C and the unchanged-status error, each keeping its exit code. `status_after` is `null` if the ticket cannot be read. If the usage file is missing or invalid (not JSON, not the expected shape, or an entry missing a field), write `models` null and warn on stderr. A failure to write the log warns on stderr and does not change the exit code.

Out of scope: anything in the Pi extension, and any report.

## Acceptance Criteria

- [ ] Tests show a line still written, with `models` null and a warning on stderr, for a missing and an invalid usage file
- [ ] Tests show `status_after` correct and the exit code kept for an agent that exits non-zero, a Ctrl-C and an unchanged status

## History

- 2026-11-04T15:11:30Z mellow-newt → todo
