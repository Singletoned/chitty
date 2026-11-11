---
title: Make `make release` wait for the publish workflow
status: backlog
labels:
  - plan-next
created: 2026-11-11
---

## Description

- After the push, find the workflow run for the tag and wait with `gh run watch <id> --exit-status`.
- Success: `uv tool upgrade chitty`, retrying briefly while PyPI catches up.
- Failure: record it with `sump capture chitty`, so `chitty fetch-errors` picks it up.

## Notes

Implemented directly as a small change (human approved, 2026-11-11) in 8c31fbd: `scripts/watch_release.py`, tested by `tests/test_watch_release.py` with fake `gh`, `uv` and `sump`. Unverified until the next real `make release`.

## History

- 2026-11-11T10:02:53Z jolly-heron → backlog
- 2026-11-11T10:24:36Z vivid-yellowhammer: changed notes
- 2026-11-11T10:24:37Z vivid-yellowhammer backlog → archived
