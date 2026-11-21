---
title: Delete `git.historical_files` and `_latest_changes`
status: done
depends_on:
  - TASK-378
  - TASK-379
  - TASK-480
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-378` (reads by rule) and `TASK-379` (numbers from `main`'s files), nothing should need the scan of every ref's history any more. Delete it, so no later change can come to depend on it. Context: `docs/plan/ticket-state.md`, "What this removes or changes" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` and `TASK-379` land.

Remove:

- From `src/chitty/git.py`: `HistoricalFile`, `historical_files`, `_latest_changes`, `_tree_blobs` and `_display_ref` (only `historical_files` uses the last three). Keep `_read_blobs`: `main_files` and `TASK-378`'s reads use it.
- From `src/chitty/store.py`: `Repo._history`, `Repo._historical_files` and its reset in `_invalidate`, and any loop over them left behind.
- `TestHistoricalFiles` in `tests/test_git.py`, and `TASK-378`'s assertion that patches `git.historical_files` to raise (in `tests/test_ticket_reads.py`): delete it, since the function is gone.

If a caller other than those `TASK-378` and `TASK-379` replaced still uses them, stop and return the ticket to `planning` naming it.

No property: a change that only removes code; the existing tests cover what remains, chiefly `tests/test_ticket_reads.py` (`TASK-378`) and `tests/test_next_number_main.py` (`TASK-379`).

## Acceptance Criteria

- [x] `git grep -nE 'historical_files|_latest_changes|HistoricalFile|_tree_blobs|_display_ref|_history\(\)' -- src tests` prints nothing
- [x] `.venv/bin/python -m unittest tests.test_ticket_reads tests.test_next_number_main` runs a non-zero number of tests and passes, and `make check` passes

## Plan

Remove the obsolete history scan and its dedicated tests, update remaining assertions that reference the removed API, then run the specified tests and full checks.

## Notes

Planning 2026-11-20: `TASK-378` was split; listing (`_tasks_in_location`, the last `_history()` caller) is now `TASK-480`, so this also waits for it.

Reviewed:
1: pass - `git grep -nE 'historical_files|_latest_changes|HistoricalFile|_tree_blobs|_display_ref|_history\(\)' -- src tests` printed nothing.
2: pass - `.venv/bin/python -m unittest tests.test_ticket_reads tests.test_next_number_main` printed `Ran 17 tests` and `OK`; `make check` printed `Ran 984 tests` and `OK`, with ruff and pyright passing.

## Summary

Removed the historical scan and obsolete references. Focused tests and make check pass.

## History

- 2026-11-18T16:20:18Z lively-quartz-crane → backlog
- 2026-11-18T16:23:25Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:36:14Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:36:14Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:36Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:42:13Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:42:13Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:42:15Z lively-quartz-crane planning → todo
- 2026-11-20T23:04:47Z quick-pearl-lapwing: changed dependencies, notes
- 2026-11-21T20:23:42Z jolly-fawn-vole todo → doing
- 2026-11-21T20:25:19Z jolly-fawn-vole: wrote the plan
- 2026-11-21T20:26:59Z jolly-fawn-vole: changed summary
- 2026-11-21T20:27:01Z jolly-fawn-vole doing → review
- 2026-11-21T20:31:07Z daring-yellow-quail: changed notes; ticked acceptance criteria
- 2026-11-21T20:31:07Z daring-yellow-quail review → done
