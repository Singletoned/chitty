---
title: Compare versions numerically in the stale setup warning
status: todo
labels:
  - bug
priority: low
created: 2026-11-03
---

## Description

`_repo()` in `src/chitty/cli.py` compares `recorded < CHITTY_VERSION` as strings, so `0.1.9` counts as newer than `0.1.22` and the warning is lost. `store.py` already has a numeric `_version_key`. Use it here. Found by the `TASK-134` cold read.

## Acceptance Criteria

- [ ] A test shows the warning appears for a recorded `0.1.9` when the code is `0.1.22`, and fails before the fix

## History

- 2026-11-03T21:24:19Z lively-panda → todo
