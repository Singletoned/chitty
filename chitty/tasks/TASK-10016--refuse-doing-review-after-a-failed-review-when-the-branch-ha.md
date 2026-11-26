---
title: Refuse `doing -> review` after a failed review when the branch has no new code commit
status: review
priority: medium
created: 2026-11-25
moved_from: TASK-QD8H6G
---

## Description

Seen 2026-11-24 (echonomicon `TASK-217`): a review failed asking to restore three deleted tests and fix a fake. The next worker wrote a summary claiming both were done and moved the ticket to `review`, but made no code commit (`git log main..task-217` showed nothing after the review). A second reviewer had to find both problems again.

Change, in `Repo._edit_stored` (`src/chitty/store.py`, beside the `leaving_doing` and `require_clean` checks): when the ticket enters `review` from `doing`, on its own branch (`str(task_id).lower()`, as `leaving_doing` checks), and its History's latest transition into `doing` came from `review`, refuse unless `HEAD` has a commit made after that transition whose subject does not start with `chitty: ` (Chitty's bookkeeping commits all do). Read the transition time from the History line; read commits with one `git log --format=%at %s` (author time: the runner rebases the branch onto `main` before each session, which rewrites committer times but keeps author times). "After" means strictly later, in whole seconds, as History records them. Put the decision in a pure `has_fix_since(failed_at, commits)` so it can be tested directly.

No escape option: a worker who thinks the review was wrong returns the ticket to `planning` with a note.

Out of scope: tickets that skip the work review (`untestable`), which never go `review -> doing` this way; runner-driven sessions need nothing extra because they use the same edit.

## Acceptance Criteria

- [ ] A Hypothesis property test of a pure `has_fix_since(failed_at, commits)` in `src/chitty/store.py` (`commits` a list of `(authored_at, subject)`): it is true exactly when some commit is authored strictly later than `failed_at` and its subject does not start with `chitty: `. Fails today (the name does not exist; stub it so the test fails on its assertion).
- [ ] A real-Git test on branch `task-1`: after `review -> doing` with a `Review failed (work):` note and only Chitty bookkeeping commits since, `chitty edit TASK-1 -s review` exits 1 with `cannot move TASK-1 to review: no commit since the failed review at <time>; commit the fix first` and changes nothing. It still refuses after `main` gains a commit and `task-1` is rebased onto it (the rebased code commits are older fixes). After one new code commit it succeeds. Fails today: the first move succeeds.
- [ ] Regression tests: a first move to `review` (no earlier failed review) works as today; existing review and status tests pass; `make check` passes.

## Plan

Use the latest timed transition into doing and Git author timestamps to reject a repeat review without a subsequent non-bookkeeping commit. Add a property test and a real-Git CLI regression covering rebase and first review, then run formatting and checks.

## Notes

Confirmed both new tests fail before the fix: the stub property assertion and the first CLI refusal (which instead succeeded).

Decided: commits to inspect -> main..HEAD, because a new main commit after review is not a fix on the ticket branch and must not bypass the rebase regression.

## Summary

Reject repeat review on the ticket branch unless a non-bookkeeping branch commit has a later author timestamp than the latest review-to-doing transition. Added property and real-Git rebase coverage and updated review fixtures. make check passes.

## History

- 2026-11-25T22:28:50Z calm-ochre-quail → backlog
- 2026-11-25T22:28:51Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:32Z calm-ochre-quail: changed title, priority
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-QD8H6G
- 2026-11-26T00:22:23Z calm-ochre-quail: replaced notes; changed description, acceptance criteria
- 2026-11-26T00:22:23Z calm-ochre-quail backlog → planning
- 2026-11-26T00:22:29Z calm-ochre-quail planning → cold-read
- 2026-11-26T00:23:27Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T00:23:27Z calm-ochre-quail cold-read → planning
- 2026-11-26T00:23:34Z calm-ochre-quail planning → todo
- 2026-11-26T01:25:59Z rosy-jade-marten todo → doing
- 2026-11-26T01:29:56Z rosy-jade-marten: wrote the plan
- 2026-11-26T01:30:38Z rosy-jade-marten: changed notes
- 2026-11-26T01:31:02Z rosy-jade-marten: changed notes
- 2026-11-26T01:37:52Z rosy-jade-marten: changed summary
- 2026-11-26T01:40:14Z rosy-jade-marten doing → review
