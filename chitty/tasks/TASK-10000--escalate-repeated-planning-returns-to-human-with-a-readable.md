---
title: Escalate repeated planning returns to human with a readable summary
status: doing
created: 2026-11-25
moved_from: TASK-D92QA4
---

## Description

In `src/chitty/store.py`, mirror `REVIEW_FAILURE_LIMIT` for repeated returns to `planning`, and set `Edit.summary` on human escalations so a person can see why a ticket stopped without reading all notes:

- Add `PLANNING_RETURN_LIMIT = 3`.
- In `check_edit()`, when `returning_to_planning` (`doing` or `review` → `planning`), count `("doing", "planning")` and `("review", "planning")` transitions in `task.transitions()` since the last transition with `new == "blocked"` (including the current one).
- Below `PLANNING_RETURN_LIMIT`, keep existing behaviour (`owner=""`, status `planning`).
- At or above `PLANNING_RETURN_LIMIT`, escalate to `status="blocked"`, `owner="human"`, append an escalation note, and set `summary` (unless the caller supplied a non-empty `edit.summary`) with the return count and the first non-empty line from incoming `(edit.note, *edit.notes)` before appending the escalation note.
- On repeated review-failure escalation (`REVIEW_FAILURE_LIMIT`), set `summary` the same way (keeping the existing escalation note wording; if incoming `(edit.note, *edit.notes)` has no non-empty line, omit that part rather than crashing).
- In `src/chitty/cli.py` (`edit`), widen `escalated = status == "doing" and ...` to `status in {"doing", "planning"}`.

Out of scope: changing `REVIEW_FAILURE_LIMIT` or `chitty run` selection logic.

## Acceptance Criteria

- [ ] In `src/chitty/store.py`, `check_edit()` keeps `status="planning"` and `owner=""` below `PLANNING_RETURN_LIMIT` and escalates to `status="blocked"`, `owner="human"`, an escalation note, and `summary` (containing the return count and first non-empty line of incoming `(edit.note, *edit.notes)`, preserving a non-empty caller-supplied `summary`) at or above `PLANNING_RETURN_LIMIT`, resetting after any transition to `blocked`. Verified by Hypothesis property tests in `tests/test_check_edit.py` varying transition history, incoming status (`doing` or `review`), and caller-supplied `summary`.
- [ ] In `src/chitty/store.py`, `check_edit()` sets `summary` the same way on repeated review-failure escalations (`REVIEW_FAILURE_LIMIT`), leaving `summary` unchanged below the limit and handling an empty incoming note on `done → doing` without crashing, and `src/chitty/cli.py` prints `escalated to human review` for escalated `planning` edits too. Verified by tests in `tests/test_check_edit.py` (and a CLI test for `planning` escalation).

## Plan

Add property and CLI tests for planning and review escalation, then implement shared escalation summaries and reset-aware planning counts; format, check, and hand off for review.

## History

- 2026-11-25T18:20:06Z human → cold-read
- 2026-11-25T18:22:23Z human: changed description, acceptance criteria
- 2026-11-25T18:22:23Z human cold-read → todo
- 2026-11-25T18:32:36Z human: renumbered from TASK-D92QA4
- 2026-11-25T20:39:10Z witty-teal-urchin todo → doing
- 2026-11-25T20:43:09Z witty-teal-urchin: wrote the plan
