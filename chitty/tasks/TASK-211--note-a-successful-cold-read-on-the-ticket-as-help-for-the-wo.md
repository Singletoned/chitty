---
title: Note a successful cold read on the ticket as help for the worker
status: done
created: 2026-11-06
---

## Description

When an implementing cold read against the current ticket text succeeds (its fail-first tests fail on the main branch and pass after its change, and it has no unresolved serious findings), the planning guide should tell the planner to add a ticket note pointing at the kept ref (`refs/cold-read/<ID>/<n>`), with the diff command, as a possible starting point for the worker, and a reminder to check it against the criteria rather than trust it.

The guide should also say to delete refs from reads made against superseded ticket text (`git update-ref -d refs/cold-read/<ID>/<n>`). The note gives `git diff <main-branch>...refs/cold-read/<ID>/<n>` with `<main-branch>` being the repository’s configured main branch. The proposed warning on notes added by non-claimants to `doing` or `done` tickets is out of scope for this guide-only change. Their tests pass, so a worker could trust them and copy behaviour the ticket has since changed.

Seen in echonomicon: `TASK-56` had three reads. The first two implemented a rule that a later finding replaced ("no word starts before the cut" became "no word ends before it"). Only the third matched the final ticket, and nothing on the ticket said which one to use.

A related gap: a planner can add notes after another session has already claimed or finished a ticket. In echonomicon, a note offering the worker a starting point landed on `TASK-56` after it was merged, and `TASK-57` had moved to a worktree in `doing`. It might help if `chitty edit --note` warned when the ticket is `doing` or `done` and the actor is not its claimant.

## Acceptance Criteria

- [x] A fail-first guide test verifies `chitty guide plan` tells planners to note a successful ref from a read of the current ticket with no serious findings, include a diff against the configured main branch, warn the worker to check the current criteria, and delete superseded refs; `make check` passes.

## Plan

Inspect the planning role guide and its tests, run the focused regression test before changes, then update the guide to give the successful-current-read note, configured-main diff, criteria warning, and stale-ref deletion instructions. Run format and make check, then record verification and hand off for review.

## Notes

Suggestion origin: echonomicon

Cold-read finding: define a successful ref as one implemented against the current ticket text with no unresolved serious findings. The non-claimant `doing`/`done` note warning is a separate feature and out of scope. Require a guide regression test that fails before the fix. Clarify the diff command uses the configured main branch.

Resolved the cold-read ambiguity in the description; the guide handoff is only for a successful read against the current ticket and the stale-note warning is out of scope.

Implementing cold read against the revised ticket: guide regression test first failed with missing current-text/no-serious-findings, diff, current-criteria and stale-ref-deletion instructions. After the guide change the focused test and `make check` passed (377 Python tests, Node tests). Candidate at `refs/cold-read/TASK-211/1`; inspect with `git diff main...refs/cold-read/TASK-211/1` and check against the current criteria before reuse. No remaining serious finding.

Added the plan-guide handoff and regression test. Confirmed the new test failed before the guide change; `make format && make check` passes (378 Python tests and Node tests). Candidate read ref is `refs/cold-read/TASK-211/1`; inspect with `git diff main...refs/cold-read/TASK-211/1` and check against current criteria before reuse. No unresolved serious finding.

Review failed (work): the worktree has uncommitted changes: `src/chitty/roles/plan.md`, `tests/test_guide_plan.py`.

Verified the focused guide regression test and full make format && make check; all passed (378 Python tests and Node tests). The prior implementation record confirms the test failed before the guide change. Kept guide changes and regression test are ready for review.

Review failed (work): the worktree has uncommitted changes: `src/chitty/roles/plan.md`, `tests/test_guide_plan.py`.

Review failed (work): the worktree has uncommitted changes: `src/chitty/roles/plan.md`, `tests/test_guide_plan.py`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Human unblock: committed the guide and regression test as 3629720 (Task: TASK-211), then merged current main. Working tree is clean; make format and make check pass (386 Python tests plus Node tests). Ready for independent review.

Reviewed:
1: pass - Guide and regression cover the current read, configured main diff, criteria warning, and superseded refs. The regression failed against the prior guide and passed against the updated guide; `make format && make check` passed (398 Python tests and Node tests).

## Summary

Guide change and regression test are ready for review. Verification: focused test passed; make format and make check passed (378 Python tests and Node tests). Follow-up: reviewer should confirm wording and criteria.

## History

- 2026-11-06T13:58:02Z youthful-toad → backlog
- 2026-11-06T13:58:03Z youthful-toad: changed notes
- 2026-11-08T14:15:13Z eager-puffin: changed notes
- 2026-11-08T14:15:30Z eager-puffin: changed description
- 2026-11-08T14:15:32Z eager-puffin: changed description
- 2026-11-08T14:15:34Z eager-puffin: changed acceptance criteria, notes
- 2026-11-08T14:19:36Z eager-puffin: changed notes
- 2026-11-08T14:19:39Z eager-puffin backlog → todo
- 2026-11-08T16:42:34Z lively-zander todo → doing
- 2026-11-08T16:42:51Z lively-zander: wrote the plan
- 2026-11-08T16:44:20Z lively-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-08T16:44:24Z lively-zander: changed summary
- 2026-11-08T16:44:24Z lively-zander doing → review
- 2026-11-08T17:15:10Z open-kestrel: changed notes
- 2026-11-08T17:15:10Z open-kestrel review → doing
- 2026-11-08T17:23:20Z lively-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-08T17:23:21Z lively-raven doing → review
- 2026-11-08T17:23:45Z intrepid-jay: changed notes
- 2026-11-08T17:23:45Z intrepid-jay review → doing
- 2026-11-08T17:26:55Z calm-heron: changed summary
- 2026-11-08T17:29:39Z calm-heron doing → review
- 2026-11-08T17:32:43Z sunny-marten: changed owner, notes
- 2026-11-08T17:32:43Z sunny-marten review → blocked
- 2026-11-08T17:57:36Z eager-puffin: changed owner, notes
- 2026-11-08T17:57:36Z eager-puffin blocked → review
- 2026-11-08T18:18:15Z vivid-crane: changed notes; ticked acceptance criteria
- 2026-11-08T18:18:15Z vivid-crane review → done
