---
title: Do not count review edits as work for review independence
status: done
labels:
  - bug
parent: TASK-283
created: 2026-11-11
---

## Description

- `Task.review_work` in `src/chitty/model.py` counts every `ticked acceptance criteria` event by an actor as work. A reviewer who ticks criteria while the ticket is in `review` is then refused its own verdict transition (seen on TASK-85 in echonomicon).
- Count a tick only if the ticket was not in `review` when it was made, which the History lines before it show. Use line order, not timestamps: one edit writes its event line before its transition line, in the same second, so a tick counts as made in the status its edit started from. A tick in the edit that moves `review` → `doing` or `done` is not counted. `wrote the plan` and moves to `review` count as now.

## Acceptance Criteria

- [x] A test: actor A moves a ticket to `review`, actor B ticks a criterion while it is in `review`, then B moves it to `doing` with a failed-review note; the move succeeds. It fails today.
- [x] A tick made by an actor while the ticket was in `doing` still counts as work, as today.
- [x] A `wrote the plan` by the reviewer while the ticket is in `review` still blocks that reviewer's verdict, as today.

## Plan

Track status across History lines in order. Count criterion ticks only when the edit started outside review, while preserving plan-write review independence checks. Add store regression tests for each specified scenario.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-286/1`. Check it against the current criteria; do not trust it.

Regression test 1 failed without the model change with reviewer cannot review this task: ticked acceptance criteria. Restored fix; focused tests and make check pass.

Reviewed: make format && make check passed: 499 Python tests, pyright, ruff and Node tests.
1: pass - test_tick_made_during_review_does_not_block_the_reviewers_verdict passes; with main model it printed reviewer cannot review this task: ticked acceptance criteria and failed.
2: pass - test_tick_made_during_doing_still_blocks_the_reviewer passed in make check.
3: pass - test_plan_written_during_review_still_blocks_the_reviewer passed in make check.

## Summary

Implemented History-order status tracking so ticks from review edits do not count as independent work; plan writes and non-review ticks still count. Verified with focused store tests and make format && make check (495 tests and Node tests). Regression confirmed failing without fix. No follow-ups.

## History

- 2026-11-11T16:09:09Z vivid-yellowhammer → backlog
- 2026-11-11T16:09:47Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T16:13:30Z vivid-yellowhammer: changed description
- 2026-11-11T16:13:31Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T16:13:31Z vivid-yellowhammer cold-read → todo
- 2026-11-11T21:09:26Z witty-dusky-toad todo → doing
- 2026-11-11T21:09:43Z witty-dusky-toad: wrote the plan
- 2026-11-11T21:37:35Z sunny-bronze-lapwing: wrote the plan
- 2026-11-11T21:39:14Z sunny-bronze-lapwing: changed notes, summary; ticked acceptance criteria
- 2026-11-11T21:39:14Z sunny-bronze-lapwing doing → review
- 2026-11-11T21:43:05Z able-navy-raven: changed notes; ticked acceptance criteria
- 2026-11-11T21:43:05Z able-navy-raven review → done
