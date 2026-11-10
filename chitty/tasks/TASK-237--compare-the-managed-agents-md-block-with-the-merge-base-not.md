---
title: Compare the managed `AGENTS.md` block with the merge-base, not main
status: doing
priority: high
created: 2026-11-10
---

## Description

`_changed_agents_block` (`src/chitty/run.py:539`) compares the managed Chitty block in the branch's `AGENTS.md` with the block on the tip of the main branch. When main refreshes its setup with `chitty init` after a ticket branch was created, the untouched branch still holds the old block, so landing (`run.py:697`, which checks before merging main at `run.py:701`) refuses it with "the branch changes Chitty's managed block", though the branch never touched it. The review gate (`run.py:511`) is unaffected because it merges main first (`run.py:492`); the new rule is a no-op there. Seen in Echonomicon on TASK-39, whose branch was already an ancestor of main.

Decision: report a change only when the branch's block differs from the block at the merge-base of the main branch and `HEAD`, the same base `_changed_config` uses with `main...HEAD`. Apply the same rule when `AGENTS.md` is missing on one side, and still report a block that does not parse on the branch. Reading the merge-base file belongs in `src/chitty/git.py` next to `file_at`.

If the branch and main share no merge-base, raise `ChittyError` naming both refs. Keep the optional `main_branch` parameter as it is.

Criterion 3 needs its own setup: `TestLanding.setUp` creates no `AGENTS.md`, so run `chitty init` on main and commit, create the ticket branch and worktree at that commit, then change the managed block on main.

Out of scope: cleaning up stale worktrees automatically, rewording the error messages.

Existing tests: `tests/test_review_merge.py` (around line 141) and `tests/test_landing.py`.

## Acceptance Criteria

- [x] A test creates a ticket branch, then commits a changed managed block on main; `_changed_agents_block` on the untouched branch returns `False`. The test fails before the fix.
- [x] A test where the branch itself edits the managed block still returns `True`, including when main has also changed it since the branch was created.
- [x] A test in `tests/test_landing.py` lands a ticket whose branch predates a managed-block change on main; main is fast-forwarded and keeps the newer block.

## Plan

Add a git helper beside file_at that resolves the merge-base of the supplied refs, raises ChittyError naming both refs when none exists, and reads the requested file at that commit. Update _changed_agents_block to compare the branch block with the merge-base block while retaining malformed-branch detection and existing missing-file semantics. Add regression coverage for a main-only managed-block refresh and landing, plus the existing branch-edit guard; run the focused tests before the fix, then make check/format.

## Notes

Cold read 1 (Haiku): fixed: the review gate merges main before the check, so only landing refuses; description corrected. Fixed: no merge-base now raises `ChittyError`; criterion 3 setup described. Decided: keep the `main_branch=None` default (out of scope). Accepted: criterion 2 is a guard and passes before the fix. Possible starting point: `git diff main...refs/cold-read/TASK-237/1`; check it against the current criteria, not trust it.

Regression test confirmed failing before the fix: the untouched ticket branch was reported as changed after main refreshed the managed block. Added merge-base file lookup with explicit no-base errors; main-only refresh now passes, branch edits remain detected, and landing retains main’s refreshed block. make format and make check passed.

Review failed (tests): Add a test asserting `_changed_agents_block` returns `True` when both main and the ticket branch change the managed block. `make format && make check` passed: 425 Python tests and 27 Node tests.

1: pass - The main-only refresh regression exercises the unchanged branch.
2: fail - No test changes the managed block on both main and the ticket branch.
3: pass - The landing regression preserves the refreshed block on main.

Criterion 2 regression test is in progress. Test setup commits distinct managed-block edits on task-1 and main, but _changed_agents_block currently returns False; investigating ref/file lookup before accepting criterion.

Criterion 2 remains unverified. The test mutation is made in the branch worktree, but the test fixture subsequently reports identical AGENTS.md blobs at task-1 and its merge-base despite an asserted text mutation. Need diagnose fixture/Git setup before a valid criterion test can be completed.

Added coverage proving a branch managed-block edit is detected even after main independently changes its block. The initial failing test setup mutated main rather than task-1 because branch_for_review returns on main; corrected by explicitly switching to task-1 first. make format and make check passed (426 Python tests and Node tests).

## Summary

Handoff: Added and committed the criterion-2 regression test (8ea851c, Task: TASK-237). Verification: main-only refresh, branch-edit-after-main-refresh, and landing preservation tests pass; make format and make check pass (426 Python tests plus Node tests). Follow-up: none.

## History

- 2026-11-10T14:08:38Z jolly-heron → backlog
- 2026-11-10T14:17:35Z jolly-heron: changed description, notes
- 2026-11-10T14:17:43Z jolly-heron backlog → todo
- 2026-11-10T16:53:07Z friendly-falcon todo → doing
- 2026-11-10T16:53:33Z friendly-falcon: wrote the plan
- 2026-11-10T16:55:07Z friendly-falcon: changed notes, summary; ticked acceptance criteria
- 2026-11-10T16:55:07Z friendly-falcon doing → review
- 2026-11-10T17:47:40Z sunny-crane: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-10T17:47:40Z sunny-crane review → doing
- 2026-11-10T17:52:08Z mellow-adder: changed notes
- 2026-11-10T17:53:25Z mellow-adder: changed notes
- 2026-11-10T17:56:06Z mellow-adder: changed notes, summary; ticked acceptance criteria
