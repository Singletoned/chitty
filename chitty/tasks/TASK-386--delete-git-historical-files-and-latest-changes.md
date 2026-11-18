---
title: Delete `git.historical_files` and `_latest_changes`
status: cold-read
depends_on:
  - TASK-378
  - TASK-379
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-378` (reads by rule) and `TASK-379` (numbers from `main`'s files), nothing should need the scan of every ref's history any more. Delete it, so no later change can come to depend on it. Context: `docs/plan/ticket-state.md`, "What this removes or changes" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` and `TASK-379` land.

Remove:

- From `src/chitty/git.py`: `HistoricalFile`, `historical_files`, `_latest_changes`, and `_tree_blobs` and `_display_ref` if nothing else uses them. Keep `_read_blobs` if `TASK-378`'s reads use it.
- From `src/chitty/store.py`: `Repo._history`, `Repo._historical_files` and its reset in `_invalidate`, and any loop over them left behind.
- `TestHistoricalFiles` in `tests/test_git.py` and any other test of the removed functions.

If a caller other than those `TASK-378` and `TASK-379` replaced still uses them, stop and return the ticket to `planning` naming it.

No property: a change that only removes code; the existing tests cover what remains, chiefly `tests/test_property_ticket_reads.py` (`TASK-378`) and `tests/test_next_number_main.py` (`TASK-379`).

## Acceptance Criteria

- [ ] `git grep -nE 'historical_files|_latest_changes|HistoricalFile|_history\(\)' -- src tests` prints nothing
- [ ] `make check` passes, including `tests/test_property_ticket_reads.py` and `tests/test_next_number_main.py`

## History

- 2026-11-18T16:20:18Z lively-quartz-crane → backlog
- 2026-11-18T16:23:25Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:36:14Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:36:14Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:36Z lively-quartz-crane planning → cold-read
