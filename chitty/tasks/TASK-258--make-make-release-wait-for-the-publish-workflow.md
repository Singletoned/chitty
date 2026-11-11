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

## History

- 2026-11-11T10:02:53Z jolly-heron → backlog
