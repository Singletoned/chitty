---
title: Stop chitty run when main fails its own check
status: backlog
created: 2026-11-22
---

## Description

Split from TASK-580 (taidy, 2026-11-22). When the pre-work check fails for a todo ticket whose branch has no work, `main` itself fails the check, so every following ticket in the same `chitty run` will also go to `error`. Decide whether the run should stop instead (and whether the ticket should go back to `todo` rather than `error`). Needs a look at the run loop in `src/chitty/run.py` before planning; TASK-580 adds the message first.

## Notes

Merged from suggestion TASK-CAJV5T (echonomicon, 2026-11-25 23:49 to 2026-11-26 00:01): four tickets in a row (TASK-238, TASK-244, TASK-BCHE6A, then TASK-226 at review) went to `error` with "check exited with status 2 ... the branch has no work yet, so `main` fails this check". One flaky Hypothesis deadline on `main` under parallel-check load caused all four; cleanup meant rebasing four branches and resetting four statuses by hand. Its proposals: on a no-work check failure, stop picking tickets, report once and leave the ticket in its previous status; optionally rerun a failing check once and record a pass as flaky; optionally let `chitty run --errors` reset a batch with the same failure. The flaky-rerun idea overlaps TASK-496.

## History

- 2026-11-22T13:19:33Z friendly-jade-stoat → todo
- 2026-11-22T13:19:39Z friendly-jade-stoat todo → backlog
- 2026-11-26T10:56:36Z calm-ochre-quail: changed notes
