---
title: Handle review tickets whose branch no longer exists
status: done
labels:
  - bug
priority: medium
created: 2026-11-13
---

## Description

On 2026-11-09 in `circuitry`, `uv run chitty run --loop --mode review -- --model gpt-6.1-terra` selected `CIRCUIT-67` and stopped with `review ticket CIRCUIT-67 has no branch circuit-67`. A review ticket can outlive its branch after manual branch deletion or cleanup. The review loop should not launch an agent for a missing branch or repeatedly select the same unrecoverable ticket; it should mark the ticket `blocked` with an actionable note naming the missing branch so a person can restore the branch or choose the ticket’s final state.

## Acceptance Criteria

- [x] A real-Git regression test creates a review ticket, deletes its expected branch, runs review selection, and fails against the current implementation before the fix.
- [x] When a review ticket’s branch is missing, `chitty run --mode review` moves the ticket to `blocked` with a note naming the ticket and branch, without launching the reviewer.
- [x] A subsequent review loop does not select the blocked ticket again, and existing review and loop checks pass.

## Plan

Add a real-Git regression in the review merge tests that deletes the review branch, invokes review mode, and verifies the ticket is blocked with an actionable note and no reviewer launch; verify a second selection skips it. Run the regression before changing behavior. Then handle the missing-branch condition at review worktree preparation by updating the ticket through Repo and returning a status result, while preserving errors for other worktree failures. Run focused review/loop tests, format, and full checks; commit the implementation and update the ticket with verified criteria and handoff.

## Notes

Cold read 1 by a fresh Sonnet subagent, `refs/cold-read/TASK-314/1`; the real-Git regression failed before the fix with `Error: review ticket TASK-1 has no branch task-1`, then the focused test passed after the fix. Review and loop suites passed (28 tests). The reader found no serious findings, open decisions, surviving mutants, or missed properties. Starting point to inspect, not trust: `src/chitty/run.py` and `tests/test_review_merge.py` from `git show refs/cold-read/TASK-314/1:<path>`. Full `make check` was blocked in the detached environment by pre-existing missing `mcp`/`mcp_types` imports in pyright.

The real-Git missing-branch regression failed before the fix with `review ticket TASK-1 has no branch task-1`. The new behavior blocks it, names the ticket and branch, skips reviewer launch, and the next review selection reports no ticket.

Verification: `make format && make check` passed, including 523 Python tests and Node tests. A real-Git test fails before the fix and passes after it; blocked review is not selected again.

Reviewed:
1: pass - The real-Git test `tests.test_review_merge.TestReviewMerge.test_missing_review_branch_blocks_ticket_and_is_not_selected_again` on the parent implementation failed with `Error: review ticket TASK-1 has no branch task-1`; on this branch it ran 1 test and printed `OK`.
2: pass - The same test printed `OK` and asserts `TASK-1: review → blocked`, the ticket and branch in the actionable note, and no agent launch.
3: pass - The same test printed `OK` and asserts the next review selection prints `no next ticket for --mode review`; `make format && make check` passed, including 523 Python tests and Node tests.

## Summary

Review tickets with missing branches are now blocked on main before reviewer command validation or launch, with a human-owned note naming the ticket and missing branch and directing a person to restore it or choose its final state. Added real-Git coverage for missing branch handling, no agent launch, and subsequent review selection; updated the prior unbranched-review expectation. Verified: `make format && make check` passes. No follow-up known.

## History

- 2026-11-13T13:32:42Z lively-violet-puffin → backlog
- 2026-11-13T13:32:50Z lively-violet-puffin backlog → cold-read
- 2026-11-13T13:35:55Z lively-violet-puffin: changed notes
- 2026-11-13T13:35:55Z lively-violet-puffin cold-read → planning
- 2026-11-13T13:35:57Z lively-violet-puffin planning → todo
- 2026-11-13T13:37:56Z quick-pearl-zander todo → doing
- 2026-11-13T13:38:17Z quick-pearl-zander: wrote the plan
- 2026-11-13T13:43:06Z quick-pearl-zander: changed notes
- 2026-11-13T13:44:05Z quick-pearl-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-13T13:44:11Z quick-pearl-zander doing → review
- 2026-11-13T13:46:28Z lively-ginger-quail: changed notes; ticked acceptance criteria
- 2026-11-13T13:46:28Z lively-ginger-quail review → done
