---
title: Retire cold-read refs and implementing-read starting points
status: planning
depends_on:
  - TASK-336
created: 2026-11-16
---

## Description

Once cold reads are read-only (`TASK-336`, which also removes the guide text about `refs/cold-read`), nothing creates cold-read refs or `cold-read/` branches. Remove `_is_cold_read_ref` and its filter in `src/chitty/git.py`, and the tests in `tests/test_cli.py` that only exist for it. Depends on `TASK-336`.

## History

- 2026-11-16T09:50:18Z intrepid-coral-raven → backlog
- 2026-11-16T09:50:27Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:25Z intrepid-coral-raven backlog → planning
- 2026-11-16T12:51:10Z open-russet-eel: changed description
