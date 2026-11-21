---
title: Use the ticket branch `task-1` in the cross-branch write tests
status: cold-read
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

To check "after": `git worktree add --detach <dir> spike/task-378`, apply `TASK-504`'s change to `_choose_source` there (or, once `TASK-504` has landed, rebase the spike onto `main`), copy the two changed test files in, and run `python -m unittest tests.test_cli.TestCrossBranchWrites tests.test_mcp.TestMcp.test_cross_branch_write_error_matches_the_cli` with `PYTHONPATH=src`.

## Acceptance Criteria

- [ ] `git diff main -- tests` changes only `tests/test_cli.py` (`TestCrossBranchWrites`) and `tests/test_mcp.py` (`test_cross_branch_write_error_matches_the_cli`), and every changed line differs only by `worker` becoming `task-1`; no `"worker"` literal is left in those five `test_cli.py` tests or that MCP test
- [ ] `make check` passes, and a note records the changed tests passing on `spike/task-378` with `TASK-504`'s change, run as the Description says

## History

- 2026-11-21T11:38:15Z sunny-ebony-kestrel → planning
- 2026-11-21T11:38:35Z sunny-ebony-kestrel: changed acceptance criteria
- 2026-11-21T11:38:35Z sunny-ebony-kestrel planning → cold-read
