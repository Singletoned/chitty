---
title: Stop `chitty run --mode work` looping on a ticket whose check fails
status: doing
labels:
  - bug
priority: high
created: 2026-11-07
---

## Description

In work mode, `chitty run` runs the configured `check` in the ticket worktree before starting the agent (`_run_check`, `src/chitty/run.py:160` and `run.py:592`). When the check fails, `_fail_check` (`run.py:630`) adds a `Review failed (work)` note, moves the ticket to `doing`, starts no agent, and exits 0. In work mode nobody else will fix the branch, so `while uv run chitty run --mode work || [ $? -eq 3 ]; do sleep 60; done` picks the same ticket every minute. This was seen with `TASK-179` (54 times) on 2026-11-07 and `TASK-131` on 2026-11-08. `REVIEW_FAILURE_LIMIT` never stops it, because `_escalate_repeated_failure` counts only review → `doing` moves.

Decided with the human on 2026-11-08:
- In both cases below, `<detail>` is the text `_run_check` already builds: `check exited with status N:` plus the last 20 output lines fenced with `_code_block`, or `check command not found: X` when the executable is missing.
- Work mode, ticket already `doing`: the failing check is the worker's job to fix. Add the note `Check failed before this session: <detail>` with a note-only `Edit` (no status, so History records no transition). Then start the agent as usual, with the claim step unchanged. Do not use the `Review failed` wording, so the note is not mistaken for a review verdict.
- Work mode, ticket in `todo`: no agent can fix it in this run. On a new branch the failure is `main`'s; on an existing branch (which `_worktree` reuses) it is that branch's. Raise `ChittyError` (exit 1) with `check failed before <ID> started: <detail>`. Change nothing in the ticket and start no agent. Leave the worktree and branch in place.
- Review mode is unchanged.

This changes `test_run_check_failure_records_output_and_does_not_claim_or_start_agent` in `tests/test_next.py`, which runs work mode on a `todo` ticket. It must now expect exit 1, no note and status `todo`. `test_run_check_failure_records_markdown_like_output`, next to it, does the same and needs the same change.

Out of scope: limiting how many work sessions a `doing` ticket gets, and the setup step's failures.

## Acceptance Criteria

- [ ] A new test in `tests/test_next.py` runs `chitty run --mode work` on a `doing` ticket that has its own branch (set up as in `test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review`), with a failing check. It asserts the agent started (the `started` file the fake agent writes), the status is still `doing`, and the notes contain `Check failed before this session` with the check output inside a fence. A fake agent that changes nothing makes the run exit 1 with `was unchanged`; the test may assert that. Record that it failed before the fix.
- [ ] The two existing `todo` check-failure tests named in the Description expect exit 1 with `check failed before TASK-1 started` and the check output in stderr, status `todo`, no new note, and no `started` file. Record that they failed before the fix.
- [ ] `PLAN.md` (`chitty run` section, step 5 and the paragraph after it) and `README.md` (around line 146) describe the two work-mode cases, and `make check` passes.

## Notes

Needs the human's decision on the proposal before refining and a cold read.

The human adopted the proposal on 2026-11-08. Refined to it; cold read next.

Cold read 1 (Haiku, `refs/cold-read/TASK-227/1`): implemented; all three tests failed first, `make check` passed. Outcomes:
1. `_fail_check` is at `run.py:630`, not 622. Fixed.
2. A `todo` ticket can have an existing branch, so `check failed on main` could blame the wrong place. Fixed: the message is `check failed before <ID> started`, and the Description names both cases.
3. A missing check executable gives `check command not found: X`, not `check exited with status N`. Fixed: both cases use `<detail>`, defined as `_run_check`'s existing text.
4. Whether the `todo` error is fenced. Fixed: it uses the same `<detail>`, so it is.
5. The new test's exit status was unstated. Fixed: a do-nothing fake agent exits 1 with `was unchanged`, and the criterion says so.
6. Whether the `doing` note changes status. Fixed: a note-only `Edit`.
The reader had to guess at 4, 5 and 6, so those were the gaps a weaker model hit. None changed the design, so no second read.

## History

- 2026-11-07T09:40:12Z vivid-dormouse → backlog
- 2026-11-08T11:10:30Z calm-eel: changed description, acceptance criteria, notes
- 2026-11-08T11:20:25Z calm-eel: changed description, acceptance criteria, notes
- 2026-11-08T11:20:25Z calm-eel backlog → todo
- 2026-11-08T11:23:24Z intrepid-marten todo → doing
