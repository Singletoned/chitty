---
title: Use the ticket branch `task-1` in the cross-branch write tests
status: review
priority: high
parent: TASK-376
created: 2026-11-21
---

## Description

Split from `TASK-378` on 2026-11-21, because three workers found that ticket too large for one session. This is a test-only change that lands before the switch, so `TASK-378` has fewer migrations to make.

The cross-branch write tests make their branch `worker`. Once `TASK-378` reads each ticket from its own branch (`task-<n>`), a ticket's newer copy on a branch called `worker` is no longer read, so those tests stop testing what they say. Renaming the branch to `task-1`, the ticket's own branch name, keeps them meaningful. Measured 2026-11-21 in scratch worktrees: after the rename, every test below passes both on `main` and on spike `ab2ac7bf` (branch `spike/task-378`) plus `TASK-504`'s change.

Change only string literals, as a pure substitution, in these places:

- `tests/test_cli.py`, class `TestCrossBranchWrites` (starts at line 1770): in `test_refuses_all_single_ticket_writes_from_another_worktree`, `test_refuses_a_branch_without_a_worktree`, `test_refuses_a_remote_tracking_branch`, `test_allows_writes_in_the_branch_with_the_latest_version` and `test_allows_writes_from_a_new_worktree_with_no_commits_of_its_own`, replace `"worker"` with `"task-1"`. That covers the worktree directory (`self.tmp / "worker"`), the branch in `git worktree add`, `checkout -b`, `push` and `branch -D`, and the asserted text. Replace `origin/worker` with `origin/task-1`, and `git switch worker` with `git switch task-1`. Do not rename the helper `claim_on_worker`. `test_allows_writes_when_an_earlier_sorting_branch_holds_the_same_version` (branch `aaa`) and `test_check` are unchanged.
- `tests/test_mcp.py`, `test_cross_branch_write_error_matches_the_cli` (line 194): replace `"worker"` with `"task-1"` in `git("checkout", "--quiet", "-b", "worker")` and in `assertRaisesRegex(ToolError, "worker")`. Leave the `worker` worktree at line 41, in a different helper, alone.

Out of scope: every other migration listed in `TASK-378`. This ticket is not a regression fix, so no fails-before evidence is needed. The tests must pass before and after the switch.

The "after" check is done: the planner ran these renamed tests on spike `ab2ac7bf` plus `TASK-504`'s change on 2026-11-21 and all 7 passed. Do not repeat it; it needs a second worktree, which workers must not create. `TASK-378`'s reviewer sees them run after the switch.

## Acceptance Criteria

- [ ] `git diff main...HEAD -- tests` changes only `tests/test_cli.py` (`TestCrossBranchWrites`) and `tests/test_mcp.py` (`test_cross_branch_write_error_matches_the_cli`), and every changed line differs only by `worker` becoming `task-1`; no `"worker"` string literal is left in those five `test_cli.py` tests or that MCP test (the helper name `claim_on_worker` stays)
- [ ] `make check` passes

## Plan

Replace only the specified branch string literals in the cross-branch tests, verify the diff, run chitty fix, format and make check, and hand off for review.

## Notes

The required after-switch verification mandates creating and modifying a separate detached worktree, including its `src/chitty/store.py` and test files. The session instruction permits changes only inside the ticket worktree and explicitly forbids touching other worktrees, so even nesting the detached worktree inside this one would violate that restriction. The ticket requires this exact method and does not permit an alternative. Please decide whether to authorize that worktree for verification or amend the required method. No implementation was started; after-switch verification and `make check` remain unfinished.

Planner 2026-11-21: the worker could not create the second worktree the after-switch check needed. The planner had already run it, so it is now recorded in the Description, and criterion 2 is just `make check`.

## Summary

Renamed the specified cross-branch test literals to `task-1`, preserving the helper and unrelated tests. `chitty fix` and `make format` completed; `make check` passed all 903 tests. The planner recorded the after-switch check in the description; it was not repeated.

## History

- 2026-11-21T11:38:15Z sunny-ebony-kestrel → planning
- 2026-11-21T11:38:35Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T11:38:35Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T11:39:35Z sunny-ebony-kestrel: changed description, acceptance criteria
- 2026-11-21T11:39:35Z sunny-ebony-kestrel cold-read → todo
- 2026-11-21T11:43:51Z tidy-silver-wren todo → doing
- 2026-11-21T11:47:18Z tidy-silver-wren: changed owner, notes
- 2026-11-21T11:47:18Z tidy-silver-wren doing → planning
- 2026-11-21T11:48:35Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T11:48:35Z sunny-ebony-kestrel planning → todo
- 2026-11-21T11:50:57Z tidy-russet-gannet todo → doing
- 2026-11-21T11:52:50Z tidy-russet-gannet: wrote the plan
- 2026-11-21T11:54:49Z tidy-russet-gannet: changed summary
- 2026-11-21T11:54:58Z tidy-russet-gannet doing → review
