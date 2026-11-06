---
title: Check PyPI every 100 `chitty` commands
status: doing
priority: low
depends_on:
  - TASK-159
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-159` alerts only when `pending-release` exists, which only `make release` writes, so nobody else finds out about a release. In `src/chitty/upgrade.py`, for a non-editable install with no `pending-release`, count every command that reaches the `finally`, including failed ones, in `$XDG_DATA_HOME/chitty/upgrade-count`, creating the directory if needed. The file holds an integer, and anything else counts as 0 and is rewritten, so a bad file cannot stop checks for good. When the count reaches `UPGRADE_CHECK_INTERVAL`, a module constant of 100, reset it and ask `PYPI_URL`. If PyPI is newer than the running version, write that version to `pending-release` with its `out` line, and run this before `TASK-159`'s steps, so its alert prints on the same command. Reset before asking, so a failed request waits for the next interval rather than slowing every command. Concurrent commands may lose a count, which does not matter. A failure here is silent, as in `TASK-159`.

## Acceptance Criteria

- [ ] Tests show earlier invocations making no request, the 100th asking and alerting when PyPI is newer, a failed request leaving nothing but a reset count, and an editable install not counting

## Plan

Add a persistent command counter in upgrade.py for non-editable installs: sanitize corrupt counts, increment commands reaching finally, and on the 100th command reset before a silent PyPI check. Run this before the existing pending-release flow so new alerts are emitted immediately. Extend tests with interval, alert, failure-reset, and editable-install cases; run formatting and make check.

## Notes

Second cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: order against `TASK-159`, a corrupt count file, the directory, and what counts.

## History

- 2026-11-04T19:36:38Z mellow-newt → backlog
- 2026-11-04T19:38:01Z mellow-newt: changed description, notes
- 2026-11-04T19:38:02Z mellow-newt backlog → todo
- 2026-11-06T00:20:39Z jolly-ibis todo → doing
- 2026-11-06T00:20:58Z jolly-ibis: wrote the plan
