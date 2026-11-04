---
title: Compare versions numerically in the stale setup warning
status: backlog
labels:
  - bug
priority: low
created: 2026-11-03
---

## Description

`_repo()` in `src/chitty/cli.py` compares `recorded < CHITTY_VERSION` as strings, so `0.1.9` counts as newer than `0.1.22` and the warning is lost. `store.py` already has a numeric `_version_key`. Use it here. Found by the `TASK-134` cold read.

## Acceptance Criteria

- [ ] A test shows the warning appears for a recorded `0.1.9` when the code is `0.1.22`, and fails before the fix

## Notes

Moved back to `backlog` on 2026-11-04, under the new rule that a ticket stays there until its cold read has outcomes. A cold read is running.

## History

- 2026-11-03T21:24:19Z lively-panda → todo
- 2026-11-04T15:30:43Z mellow-newt: changed notes
- 2026-11-04T15:30:43Z mellow-newt todo → backlog
