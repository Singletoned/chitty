---
title: Do not fail `chitty run` when a passed review removes its worktree
status: done
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

Seen on 2026-11-04 at the end of the `TASK-119` review, which passed: `Error: no Chitty configuration in .../.worktrees/task-119`. The guide tells a reviewer to merge on a pass and then remove the branch and worktree. `run` in `src/chitty/run.py` then calls `Repo.open(worktree)` to read the new status, and the directory has gone. So every passed review ends in a non-zero exit, which stops an unattended loop even though the work landed. `TASK-126` introduced this by moving Pi into the worktree, and no test has a fake agent that removes it.

After the agent exits, if the worktree no longer exists, read the status through a new `Repo.open(main_root)`, whose `find` sees the newest copy on any branch. Report the result as usual. If the branch still exists, that is simply its status, and a later run adds the worktree back. If the branch has gone too and the status on `main` is not `done`, the work has been lost, so fail with a message naming the ticket: comparing statuses would otherwise report a false `doing → todo` in work mode, and a misleading "unchanged" in review mode. `TASK-131` stops reviewers removing worktrees, but a person or an agent can still do it, so keep this.

Out of scope: landing.

## Acceptance Criteria

- [x] A test with a fake agent that merges the branch, removes the worktree and exits shows `chitty run` exiting 0 and printing the status change
- [x] Tests show a worktree removed with its branch kept reporting the branch's status, and worktree and branch both removed without a merge failing with a message naming the ticket, in work and review modes

## Plan

Inspect `run.py` lifecycle and existing run tests. Add a post-agent status lookup that falls back to `main_root` only when the worktree disappeared, while distinguishing a kept branch from a lost ticket. Add regression tests for merged removal and unmerged removal in work/review modes, then run `make check`, apply `chitty fix`, and prepare a task commit.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: my claim that the ticket must be merged, and my second criterion, which would have failed a harmless case with the branch kept. Rejected: declaring an order against `TASK-148`, which already follows through `TASK-127`.

Review failed (tests): acceptance criterion 2 is not fully demonstrated: the added tests cover merged removal and unmerged removal in work and review modes, but no test covers a removed worktree with its branch kept reporting the branch status. Add that regression test and re-run verification.

Added regression coverage for worktree removal with the branch retained in both work and review modes; the test fails against the pre-fallback implementation and passes with it.

Reviewed: inspected the implementation and all acceptance tests; targeted tests passed, make check passed (241 Python tests and Node tests), and chitty fix completed with existing warnings only.

## Summary

Added branch-retained worktree-removal regressions for work and review modes. Existing fallback handles merged removal and loudly rejects lost tickets. Verified the new regression fails against the pre-fallback implementation, passes with the fix, and make check passes (241 Python tests and Node tests).

## History

- 2026-11-04T15:12:08Z mellow-newt → todo
- 2026-11-04T15:17:30Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-05T09:51:00Z lively-marten todo → doing
- 2026-11-05T09:51:12Z lively-marten: wrote the plan
- 2026-11-05T09:57:30Z lively-marten: ticked acceptance criteria
- 2026-11-05T09:57:31Z lively-marten: ticked acceptance criteria
- 2026-11-05T09:57:32Z lively-marten: changed summary
- 2026-11-05T09:57:33Z lively-marten doing → review
- 2026-11-05T10:01:56Z vivid-dormouse: changed acceptance criteria, notes
- 2026-11-05T10:01:56Z vivid-dormouse review → doing
- 2026-11-05T10:06:51Z calm-quail: changed notes; ticked acceptance criteria
- 2026-11-05T10:06:55Z calm-quail: changed summary
- 2026-11-05T10:07:09Z calm-quail doing → review
- 2026-11-05T10:12:32Z brisk-ibis: changed notes
- 2026-11-05T10:12:32Z brisk-ibis review → done
- 2026-11-05T14:44:55Z vivid-wren done → archived
