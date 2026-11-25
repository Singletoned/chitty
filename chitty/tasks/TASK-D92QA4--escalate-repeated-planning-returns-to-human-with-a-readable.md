---
title: Escalate repeated planning returns to human with a readable summary
status: cold-read
created: 2026-11-25
provisional: true
---

## Description

In `src/chitty/store.py`, mirror `REVIEW_FAILURE_LIMIT` for repeated returns to `planning`, and set `Edit.summary` on human escalations so a person can see why a ticket stopped without reading all notes:

- Add `PLANNING_RETURN_LIMIT = 3`.
- In `check_edit()`, when `returning_to_planning` (`doing` or `review` → `planning`), count `("doing", "planning")` and `("review", "planning")` transitions in `task.transitions()` since the last transition with `new == "blocked"` (including the current one).
- Below `PLANNING_RETURN_LIMIT`, keep existing behaviour (`owner=""`, status `planning`).
- At or above `PLANNING_RETURN_LIMIT`, escalate to `status="blocked"`, `owner="human"`, append an escalation note, and set `summary` (unless the caller supplied a non-empty `edit.summary`) with the return count and the first non-empty line of the incoming note.
- In `_escalate_repeated_failure()`, also set `summary` the same way when escalating repeated review failures (keeping its existing escalation note wording).

Out of scope: changing `REVIEW_FAILURE_LIMIT` or `chitty run` selection logic.

## Acceptance Criteria

- [ ] In `src/chitty/store.py`, `check_edit()` keeps `status="planning"` and `owner=""` below `PLANNING_RETURN_LIMIT` and escalates to `status="blocked"`, `owner="human"`, an escalation note, and a non-empty `summary` at or above `PLANNING_RETURN_LIMIT` (resetting the count after any transition to `blocked`), verified by Hypothesis property tests in `tests/test_check_edit.py` varying transition history, incoming status (`doing` or `review`), and caller-supplied `summary`.
- [ ] `_escalate_repeated_failure()` in `src/chitty/store.py` sets `edit.summary` with the failure count and first non-empty line of the incoming note when escalating (preserving a non-empty caller-supplied `summary`), verified by tests in `tests/test_check_edit.py`.

## History

- 2026-11-25T18:20:06Z human → cold-read
