---
title: Stop `chitty run --mode work` looping on a ticket whose check fails
status: backlog
labels:
  - bug
priority: high
created: 2026-11-07
---

## Description

Seen on 2026-11-07: `while uv run chitty run --mode work || [ $? -eq 3 ]; do sleep 60; done` picked `TASK-179` 54 times in a row, about once a minute. Each time `_run_check` in `src/chitty/run.py` (line 582) found the branch check failing (`check_version_bump: changed files require a version above main (0.1.42), but working tree has 0.1.41`), and `_fail_check` added a `Review failed (work)` note and moved the ticket `doing` → `doing`. No agent started, so nothing fixed the branch, and `chitty run` exited 0, so the loop ran again on the same ticket. `REVIEW_FAILURE_LIMIT` never blocks it, because `_escalate_repeated_failure` only counts review → doing moves. Other tickets were starved meanwhile, including `TASK-224`, which would remove this version check.

`PLAN.md` (the `chitty run` section, step 5) says a failed check "starts no agent", which makes sense in review mode, where the work goes back to its worker. In work mode the worker is the one who would fix it.

Proposed, for the human to decide before refining:
- Work mode, ticket already `doing`: start the agent anyway, with the check output in its prompt or notes, because making the check pass is its job.
- Work mode, ticket in `todo`: its new branch is `main`, so `main` itself is broken. Exit non-zero without changing the ticket, so a loop stops.

Parked meanwhile: `TASK-179`, `TASK-181` and `TASK-193` have owner `human`.

## Notes

Needs the human's decision on the proposal before refining and a cold read.

## History

- 2026-11-07T09:40:12Z vivid-dormouse → backlog
