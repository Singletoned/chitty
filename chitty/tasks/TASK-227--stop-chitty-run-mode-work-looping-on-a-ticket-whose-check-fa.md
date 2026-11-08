---
title: Stop `chitty run --mode work` looping on a ticket whose check fails
status: backlog
labels:
  - bug
priority: high
created: 2026-11-07
---

## Description

In work mode, `chitty run` runs the configured `check` in the ticket worktree before starting the agent (`_run_check`, `src/chitty/run.py:160` and `run.py:592`). When the check fails, `_fail_check` (`run.py:622`) adds a `Review failed (work)` note, moves the ticket to `doing`, starts no agent, and exits 0. In work mode nobody else will fix the branch, so `while uv run chitty run --mode work || [ $? -eq 3 ]; do sleep 60; done` picks the same ticket every minute. This was seen with `TASK-179` (54 times) on 2026-11-07 and `TASK-131` on 2026-11-08. `REVIEW_FAILURE_LIMIT` never stops it, because `_escalate_repeated_failure` counts only review → `doing` moves.

Decided with the human on 2026-11-08:
- Work mode, ticket already `doing`: the failing check is the worker's job to fix. Add a note `Check failed before this session: check exited with status N:` followed by the output, fenced with the existing `_code_block` helper, and keep the status. Then start the agent as usual, with the claim step unchanged. Do not use the `Review failed` wording, so the note is not mistaken for a review verdict.
- Work mode, ticket in `todo`: its new branch was just made from `main`, so `main` itself fails the check. Raise `ChittyError` (exit 1) with `check failed on main before <ID> started: check exited with status N:` and the last 20 output lines. Change nothing in the ticket and start no agent. Leave the worktree and branch in place; `chitty run` already reuses an existing branch.
- Review mode is unchanged.

This changes `test_run_check_failure_records_output_and_does_not_claim_or_start_agent` in `tests/test_next.py`, which runs work mode on a `todo` ticket. It must now expect exit 1, no note and status `todo`. `test_run_check_failure_records_markdown_like_output`, next to it, does the same and needs the same change.

Out of scope: limiting how many work sessions a `doing` ticket gets, and the setup step's failures.

## Acceptance Criteria

- [ ] A new test in `tests/test_next.py` runs `chitty run --mode work` on a `doing` ticket that has its own branch, with a failing check. It asserts the agent started (as the existing tests do, through the `started` file the fake agent writes), the status is still `doing`, and the notes contain `Check failed before this session` with the check output inside a fence. Record that it failed before the fix.
- [ ] The two existing `todo` check-failure tests named in the Description expect exit 1 with `check failed on main before TASK-1 started` and the check output in stderr, status `todo`, no new note, and no `started` file. Record that they failed before the fix.
- [ ] `PLAN.md` (`chitty run` section, step 5 and the paragraph after it) and `README.md` (around line 146) describe the two work-mode cases, and `make check` passes.

## Notes

Needs the human's decision on the proposal before refining and a cold read.

The human adopted the proposal on 2026-11-08. Refined to it; cold read next.

## History

- 2026-11-07T09:40:12Z vivid-dormouse → backlog
- 2026-11-08T11:10:30Z calm-eel: changed description, acceptance criteria, notes
