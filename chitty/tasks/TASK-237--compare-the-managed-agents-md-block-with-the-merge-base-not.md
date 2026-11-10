---
title: Compare the managed `AGENTS.md` block with the merge-base, not main
status: backlog
priority: high
created: 2026-11-10
---

## Description

`_changed_agents_block` (`src/chitty/run.py:539`) compares the managed Chitty block in the branch's `AGENTS.md` with the block on the tip of the main branch. When main refreshes its setup with `chitty init` after a ticket branch was created, the untouched branch still holds the old block, so both the review gate (`run.py:511`) and landing (`run.py:697`) refuse it with "the branch changes Chitty's managed block", though the branch never touched it. Seen in Echonomicon on TASK-39, whose branch was already an ancestor of main.

Decision: report a change only when the branch's block differs from the block at the merge-base of the main branch and `HEAD`, the same base `_changed_config` uses with `main...HEAD`. Apply the same rule when `AGENTS.md` is missing on one side, and still report a block that does not parse on the branch. Reading the merge-base file belongs in `src/chitty/git.py` next to `file_at`.

Out of scope: cleaning up stale worktrees automatically, rewording the error messages.

Existing tests: `tests/test_review_merge.py` (around line 141) and `tests/test_landing.py`.

## Acceptance Criteria

- [ ] A test creates a ticket branch, then commits a changed managed block on main; `_changed_agents_block` on the untouched branch returns `False`. The test fails before the fix.
- [ ] A test where the branch itself edits the managed block still returns `True`, including when main has also changed it since the branch was created.
- [ ] A test in `tests/test_landing.py` lands a ticket whose branch predates a managed-block change on main; main is fast-forwarded and keeps the newer block.

## History

- 2026-11-10T14:08:38Z jolly-heron → backlog
