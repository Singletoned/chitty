---
title: Count a landing check failure as a failed review for escalation
status: planning
depends_on:
  - TASK-609
created: 2026-11-23
---

## Description

TASK-609 sends a ticket back to `doing` when its landing check fails after a clean rebase (the `LandingCheckFailed` handler in `src/chitty/run.py`, which calls `branch_repo.edit(action.id, Edit(status="doing", ..., skip_verdicts=True, skip_current_version=True))`). That move is `done → doing` (the reviewer had set `done`), and escalation does not see it: `_escalate_repeated_failure` (`src/chitty/store.py`) counts only `review → doing` transitions, and `check_edit` (same file) calls it only when `is_review_transition` holds, which requires the previous status `review`. A ticket whose landing check keeps failing would then cycle `doing → review → done → doing` forever instead of reaching a person after `REVIEW_FAILURE_LIMIT` (3, `store.py`) failures.

Change:

- In `check_edit`, call `_escalate_repeated_failure` when the edit moves to `doing` from `review` or from `done`. Do not add `done` to `is_review_transition` itself: that would also apply the verdict-line and reviewer-independence checks to the landing edit.
- In `_escalate_repeated_failure`, count `(done, doing)` transitions as failures alongside `(review, doing)`, still since the last move to `blocked`.

Decided: every `done → doing` counts, not only the runner's. Reopening a finished ticket by hand is rare, and it is a failure of the earlier review too; this avoids a new `Edit` flag.

Property tool: Hypothesis, as in `tests/test_check_edit.py`.

Out of scope: changing `REVIEW_FAILURE_LIMIT`, the escalation note text, or the landing failure note.

## Acceptance Criteria

- [ ] A Hypothesis property test in `tests/test_check_edit.py`, next to `test_failed_reviews_escalate_at_the_limit` and built the same way (`make_task(<status>, [], None, [])`, so the verdict check has no criteria to check, then `with_history` by `other-reviewer` for each drawn transition), draws zero to eight transitions, each independently (they need not chain, since the code reads only pairs), from `(review, doing)`, `(done, doing)`, `(doing, review)`, `(review, done)`, `(doing, blocked)` and `(blocked, doing)`, and a current status of `review` or `done`. Applying `fail_review_edit("Review failed: generated failure.")` through `check_edit(task, edit, "fresh-reviewer")` gives status `blocked` with owner `human` exactly when 1 + the number of `(review, doing)` and `(done, doing)` transitions after the last transition into `blocked` reaches `REVIEW_FAILURE_LIMIT`; otherwise status `doing`. Draws with current status `done` and two `(review, doing)` transitions fail on `main`.
- [ ] A test in `tests/test_review_merge.py`, set up like `test_failing_check_after_main_advances_preserves_main_and_worktree` but calling `self.branch_for_review(failures=2)`, runs `run --mode review` and asserts the ticket (`self.ticket()`) ends `blocked`, owner `human`, with a note starting `Escalated to human review: failed review 3 times` and the `Review failed (integration):` note. It fails on `main`, where the ticket ends `doing`.
- [ ] An example test in `tests/test_check_edit.py`: a `done` task whose history (built with `with_history`) has `(doing, review)` by `fresh-reviewer` and no failures accepts `check_edit(task, Edit(status="doing", note="Review failed (integration): x", skip_verdicts=True, skip_current_version=True), "fresh-reviewer")` with status `doing`, because the landing edit is not a review transition. The worker shows it fails if `done` is added to `is_review_transition` (the reviewer-independence check raises `cannot review this task`): make that change uncommitted, run the test, discard the change, and record the failing output in a note on this ticket.

## Notes

Planning: relies on TASK-609 (its landing-failure handler and test fixture). When TASK-609 is done, compare, cold-read, then move to `todo`.

Precedent for criterion 2: `test_automatic_and_reviewer_failures_count_together` in `tests/test_review_merge.py` covers the `review → doing` path.

## History

- 2026-11-23T10:37:53Z witty-russet-gannet → backlog
- 2026-11-23T10:39:08Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:39:08Z witty-russet-gannet backlog → planning
- 2026-11-23T10:39:10Z witty-russet-gannet: changed notes
- 2026-11-23T13:37:39Z youthful-quartz-zander: changed description
- 2026-11-23T13:37:50Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T13:37:56Z youthful-quartz-zander planning → cold-read
- 2026-11-23T13:39:25Z youthful-quartz-zander cold-read → planning
- 2026-11-23T13:39:40Z youthful-quartz-zander: changed acceptance criteria, notes
- 2026-11-23T13:40:09Z youthful-quartz-zander planning → cold-read
- 2026-11-23T13:41:41Z youthful-quartz-zander cold-read → planning
- 2026-11-23T13:41:43Z youthful-quartz-zander: changed acceptance criteria
