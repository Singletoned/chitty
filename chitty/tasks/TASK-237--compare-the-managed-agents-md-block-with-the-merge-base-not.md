---
title: Compare the managed `AGENTS.md` block with the merge-base, not main
status: backlog
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

- [ ] A test creates a ticket branch, then commits a changed managed block on main; `_changed_agents_block` on the untouched branch returns `False`. The test fails before the fix.
- [ ] A test where the branch itself edits the managed block still returns `True`, including when main has also changed it since the branch was created.
- [ ] A test in `tests/test_landing.py` lands a ticket whose branch predates a managed-block change on main; main is fast-forwarded and keeps the newer block.

## Notes

Cold read 1 (Haiku): fixed: the review gate merges main before the check, so only landing refuses; description corrected. Fixed: no merge-base now raises `ChittyError`; criterion 3 setup described. Decided: keep the `main_branch=None` default (out of scope). Accepted: criterion 2 is a guard and passes before the fix. Possible starting point: `git diff main...refs/cold-read/TASK-237/1`; check it against the current criteria, not trust it.

## History

- 2026-11-10T14:08:38Z jolly-heron → backlog
- 2026-11-10T14:17:35Z jolly-heron: changed description, notes
