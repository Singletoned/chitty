---
title: Compare versions numerically in the stale setup warning
status: todo
labels:
  - bug
priority: low
created: 2026-11-03
---

## Description

`_warn_setup_version` in `src/chitty/cli.py` compares `recorded < CHITTY_VERSION` as strings, so `0.1.9` counts as newer than `0.1.22` and the warning is lost. `store.py` already has a numeric `_version_key`. Use it here. Found by the `TASK-134` cold read.

Use `_version_key` from `src/chitty/store.py`, renaming it without the underscore now that two modules use it. It raises on a value such as `1.0rc1`, and this function runs on every command, so catch that here and warn that the recorded version cannot be read: a bad `chitty_version` should not stop reads. Writes already refuse it. Tests can use recorded values against the real version: `0.1.9` is older but sorts as newer, and `0.1.100` is newer but sorts as older.

## Acceptance Criteria

- [ ] A test shows the warning appears for a recorded `0.1.9` when the code is `0.1.22`, and fails before the fix

## Notes

Moved back to `backlog` on 2026-11-04, under the new rule that a ticket stays there until its cold read has outcomes. A cold read is running.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the function's name; which helper to use; a bad version turning a warning into a crash on every read; and the newer direction, which has the same bug. Rejected: patching `CHITTY_VERSION` in tests, because recorded values can show both directions against the real one. Moved to `todo` now the findings have outcomes.

## History

- 2026-11-03T21:24:19Z lively-panda → todo
- 2026-11-04T15:30:43Z mellow-newt: changed notes
- 2026-11-04T15:30:43Z mellow-newt todo → backlog
- 2026-11-04T15:31:49Z mellow-newt: changed description, notes
- 2026-11-04T15:31:49Z mellow-newt backlog → todo
