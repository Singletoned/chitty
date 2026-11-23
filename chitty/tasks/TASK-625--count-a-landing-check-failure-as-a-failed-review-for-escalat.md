---
title: Count a landing check failure as a failed review for escalation
status: planning
depends_on:
  - TASK-609
created: 2026-11-23
---

## Description

TASK-609 sends a ticket back to `doing` when its landing check fails after a clean rebase. That move is `done → doing` (the reviewer had set `done`), and escalation does not see it: `_escalate_repeated_failure` (`src/chitty/store.py:1656`) counts only `review → doing` transitions, and `check_edit` applies it only for review transitions (`is_review_transition`, `store.py:1585` and `1609`). A ticket whose landing check keeps failing would then cycle `doing → review → done → doing` forever instead of reaching a person after `REVIEW_FAILURE_LIMIT` (3, `store.py:72`) failures.

Change:

- In `check_edit`, apply `_escalate_repeated_failure` when the edit moves to `doing` from `review` or from `done`.
- In `_escalate_repeated_failure`, count `(done, doing)` transitions as failures alongside `(review, doing)`, still since the last move to `blocked`.

Decided: every `done → doing` counts, not only the runner's. Reopening a finished ticket by hand is rare, and it is a failure of the earlier review too; this avoids a new `Edit` flag.

Property tool: Hypothesis, as in `tests/test_check_edit.py`.

## Acceptance Criteria

- [ ] A Hypothesis property test in `tests/test_check_edit.py`, next to `test_failed_reviews_escalate_at_the_limit`, draws a history of transitions from `(review, doing)`, `(done, doing)`, `(doing, review)`, `(review, done)`, `(doing, blocked)` and `(blocked, doing)`, and a current status of `review` or `done`. Applying `fail_review_edit(...)` through `check_edit` gives `blocked` with owner `human` exactly when 1 + the number of `(review, doing)` and `(done, doing)` transitions after the last move to `blocked` reaches `REVIEW_FAILURE_LIMIT`; otherwise `doing`. Draws with current status `done` fail on `main`.
- [ ] A `tests/test_review_merge.py` test, using TASK-609's landing check failure fixture on a ticket whose history already has two `review → doing` failures, ends with the ticket `blocked`, owner `human`, and the `Escalated to human review` note.

## Notes

Planning: relies on TASK-609 (its landing-failure handler and test fixture). When TASK-609 is done, compare, cold-read, then move to `todo`.

## History

- 2026-11-23T10:37:53Z witty-russet-gannet → backlog
- 2026-11-23T10:39:08Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:39:08Z witty-russet-gannet backlog → planning
- 2026-11-23T10:39:10Z witty-russet-gannet: changed notes
