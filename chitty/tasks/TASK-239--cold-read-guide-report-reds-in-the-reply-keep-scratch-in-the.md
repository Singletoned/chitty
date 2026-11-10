---
title: "Cold-read guide: report reds in the reply, keep scratch in the worktree, filter findings"
status: review
created: 2026-11-10
---

## Description

Four additions to the cold-read guide, `src/chitty/roles/cold-read.md`, from planning mullion. Each saves the planner a round of fixes or a repeat read.

- Readers may not write to Chitty, so tickets that ask the worker to record a failing test in a note confused them. Tell readers to put red test output in their report, never in a ticket note.
- Readers wrote scratch logs to `/tmp` or the main checkout. Tell them to keep every scratch file inside the read worktree and delete it before running the check, because the check may lint stray files.
- Reads converged only once readers reported just the findings that change what a worker builds or how a reviewer verifies it, and listed choices left to the worker in one line without asking for a ticket change. Say that in the report section, as a rule over the whole list: keep the existing report items, but report an unverified behaviour, unhandled state or wrong claim only when it passes that filter.

- One reader reported its full test run as passing from the shell pipeline's exit status while the runner had printed `FAILED (failures=15, errors=261)`. Tell readers to quote the test runner's own summary line as evidence of a pass or fail, not an exit status.

Keep each addition to one or two lines. Put tests in a new `tests/test_guide_cold_read_reports.py` in the style of `tests/test_guide_plan.py` (assert phrases in the whitespace-normalised `guide("cold-read")` text).

## Acceptance Criteria

- [x] `guide("cold-read")` tells readers to put failing test output in their report, not in a ticket note.
- [x] `guide("cold-read")` tells readers to keep scratch files inside the read worktree and delete them before running the check.
- [x] `guide("cold-read")` tells readers to report only findings that change what a worker builds or how a reviewer verifies it, and to list worker choices in one line.
- [x] `guide("cold-read")` tells readers to quote the test runner's own summary line, not an exit status, as evidence that tests passed or failed.

## Plan

Update the cold-read report instructions with the four requested constraints, then add focused phrase assertions in tests/test_guide_cold_read_reports.py. Run the new test, formatter and full checks, verify each criterion, commit implementation files, and hand off the ticket for review.

## Notes

Cold read 1 (Haiku): fixed: the new filter clashed with the existing report list (unverified behaviour, wrong claims); the description now says the filter governs every report item and the list stays. Rejected: pinning exact test phrases in the ticket; repository guide tests assert phrases the worker chooses, and the reviewer checks the meaning. Possible starting point: `git diff main...refs/cold-read/TASK-239/1`; check it against the current criteria, not trust it.

Added report rules for test-summary evidence, scratch-file handling, and filtered findings; focused guide test and full make check passed.

## Summary

Implemented the four cold-read guide additions and added tests/test_guide_cold_read_reports.py. Verified focused test and full make format && make check (424 Python suites and Node tests passed). Commit: 5d2aefc. No follow-ups.

## History

- 2026-11-10T14:08:40Z jolly-heron → backlog
- 2026-11-10T14:16:57Z jolly-heron: changed description, notes
- 2026-11-10T14:17:46Z jolly-heron backlog → todo
- 2026-11-10T14:26:23Z jolly-heron: changed description, acceptance criteria
- 2026-11-10T16:58:23Z friendly-falcon todo → doing
- 2026-11-10T16:58:50Z friendly-falcon: wrote the plan
- 2026-11-10T17:00:53Z friendly-falcon: changed notes, summary; ticked acceptance criteria
- 2026-11-10T17:00:53Z friendly-falcon doing → review
