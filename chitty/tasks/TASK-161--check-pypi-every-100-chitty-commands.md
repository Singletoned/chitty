---
title: Check PyPI every 100 `chitty` commands
status: backlog
priority: low
depends_on:
  - TASK-159
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-159` alerts only when `pending-release` exists, which only `make release` writes, so nobody else finds out about a release. In `src/chitty/upgrade.py`, for a non-editable install with no `pending-release`, count invocations in `$XDG_DATA_HOME/chitty/upgrade-count`. When the count reaches `UPGRADE_CHECK_INTERVAL`, a module constant of 100, reset it and ask `PYPI_URL`. If PyPI is newer than the running version, write that version to `pending-release` with its `out` line, so the alert from `TASK-159` takes over. Reset before asking, so a failed request waits for the next interval rather than slowing every command. Concurrent commands may lose a count, which does not matter. A failure here is silent, as in `TASK-159`.

## Acceptance Criteria

- [ ] Tests show earlier invocations making no request, the 100th asking and alerting when PyPI is newer, a failed request leaving nothing but a reset count, and an editable install not counting

## History

- 2026-11-04T19:36:38Z mellow-newt → backlog
