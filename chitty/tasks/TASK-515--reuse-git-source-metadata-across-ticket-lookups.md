---
title: Reuse Git source metadata across ticket lookups
status: planning
parent: TASK-480
created: 2026-11-21
---

## Description

Before `TASK-480` uses authoritative lookups for listings, stop doing Git metadata discovery per ticket. `tests/test_list_performance.py` already requires constant Git invocation count on `main` with no ticket branches. A probe that opens one `Repo`, enumerates `ticket_ids()` and calls `lookup` for each found ID makes 16 Git calls for two tickets and 56 for ten today.

In `src/chitty/store.py`, cache the per-checkout Git repository presence, current branch, configured main tip, and branch tips on the `Repo` for source selection and ref-file discovery. Reuse the existing current-branch cache. Clear these caches at the existing `Repo._invalidate()` boundary alongside `_source_refs`, `_ticket_ref_files` and `_ticket_ids`. Preserve lazy per-ID content parsing, per-ticket ancestry/conflict checks, source precedence, and working-tree reads. No changes to `ticket_source`, listings or Git ref/blob transport. The constant process count only applies to the no-ticket-branch fixture; ancestry calls for actual branch candidates are out of scope.

Use real Git in temporary repositories. No new source-selection property: the selection logic is unchanged and already covered by `tests/test_property_ticket_source.py` and the source-copy suites. The new checks exercise process count and invalidation across real Git state changes.

## Acceptance Criteria

- [ ] Extend `tests/test_list_performance.py` with the real-Git lookup probe: for committed `main` repos with 2 and 10 distinct valid tickets and no ticket branches, a fresh subprocess opens one `Repo`, enumerates all `ticket_ids()` and successfully looks each up. Assert the expected number of IDs and lookups and equal built-in Git invocation counts from `GIT_TRACE`, as in the existing list trace test. This new equality assertion fails on the old code; keep the existing list test passing.
- [ ] In one `Repo` opened at the real `main` checkout, first look up a committed `TASK-1` with no ticket branch and check that its title is the baseline and its branch is unset. Create `task-1`, commit a title change on it, return to `main`, call `Repo._invalidate()`, and check that lookup returns the branch title and `task-1`. Fast-forward `main` to `task-1` without deleting the branch, invalidate again, and check that lookup returns the new title from the working tree with no branch. Existing source-copy and source-selection tests still pass.

## History

- 2026-11-21T15:51:38Z honest-coral-heron → backlog
- 2026-11-21T15:51:50Z honest-coral-heron backlog → planning
- 2026-11-21T15:51:52Z honest-coral-heron: changed acceptance criteria
- 2026-11-21T15:51:52Z honest-coral-heron planning → cold-read
- 2026-11-21T15:54:55Z honest-coral-heron cold-read → planning
