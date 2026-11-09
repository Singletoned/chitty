---
title: Land waiting tickets at the start of `chitty run`
status: doing
priority: medium
depends_on:
  - TASK-151
parent: TASK-106
created: 2026-11-04
---

## Description

Last part of landing, after `TASK-131`, so a ticket whose landing failed or was interrupted still lands.

A pending ticket is a non-archived `done` ticket with a local branch named `<id in lower case>`. Find it by branch name, not `StoredTask.branch`, which is `None` once the file matches `main`. Legacy branches with other names are ignored, and remote refs are never touched. If the branch has no worktree, add one as in `TASK-126`.

At the start of every `chitty run`, before selecting a ticket, land each pending ticket in ID order, stopping at the first failure. Read statuses through `Repo.find`, which sees the newest copy on any branch. A run with `--ticket` from `TASK-138` skips this, because it should touch only that ticket. A landing failure now gets another try here, which `TASK-131` could not offer. Every step is a no-op once done, so a later run repeats only what is left.

A successful landing here ends that run, printing what landed and exiting 0: the running process still holds the old code, so the next agent must start from a new `chitty run`, which refreshes setup first. A failure also stops the run, exiting non-zero. This overrides the `TASK-124` rule that a changed status exits 0, so update its tests where needed.

Out of scope: pushing.

## Acceptance Criteria

- [x] Tests show two pending tickets landing in ID order and a stop at the first failure
- [x] Tests show a leftover unfinished rebase stopping loudly, and a retry completing after a failed worktree removal
- [x] A test shows a landing at the start of a run exiting 0 without starting the agent, and the next run selecting a ticket
- [x] A test shows a landing that failed being completed by a later run once its cause is fixed

## Plan

Inspect the runner, repository/worktree helpers, and existing run tests. Add pending-ticket discovery by local branch name and ordered retry landing before selection, except for --ticket. Keep landing steps retry-safe and propagate unfinished-operation/failure errors. Add isolated regression tests for ordering, interruption/retry, and run selection behavior; update PLAN.md runner behavior. Run focused tests, then make format and make check.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: where this runs, how it reads status, and `--ticket`; took over "a later run lands it" from `TASK-131`. Rejected: an order against `TASK-136` and the others changing `src/chitty/run.py`, because one ticket is in work at a time, and each rebases on what has landed.

Verified all four criteria: pending tickets land in ID order and stop on the first failure; an unfinished rebase fails loudly, and removal failure retries; run lands before agent startup and a subsequent run selects work; a failed run completes landing on retry after the cause is removed. `make format && make check` passes (408 Python tests plus Node tests). Commit: b3f2efd.

## Summary

Implemented pending landing retries before plain-run ticket selection, using local branch names and Repo.find statuses. Tests cover ordering, stop/error retries, no-agent landing followed by selection, and retry on a later run. Verification: make format && make check passes (408 Python tests and Node tests). Follow-up: none.

## History

- 2026-11-04T15:11:36Z mellow-newt → todo
- 2026-11-04T15:17:40Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-05T10:07:35Z mellow-newt: changed description
- 2026-11-05T10:23:47Z mellow-newt: changed description
- 2026-11-09T09:33:52Z calm-adder todo → doing
- 2026-11-09T09:34:18Z calm-adder: wrote the plan
- 2026-11-09T09:49:58Z calm-adder: changed notes; ticked acceptance criteria
- 2026-11-09T09:49:59Z calm-adder: changed summary
