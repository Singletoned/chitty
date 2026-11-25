---
title: Name uncommitted worktree changes, not `main`, when the pre-check fails
status: planning
priority: high
created: 2026-11-24
---

## Description

When a reused ticket worktree holds uncommitted changes left by an earlier session, the runner's pre-check can fail on them, and the error note says "the branch has no work yet, so `main` fails this check". `main` passes; the note sends the next reader to the wrong place. Seen in echonomicon `TASK-195` and `TASK-133` (2026-11-23) and chitty `TASK-651`. `TASK-491` (0.8.0) now stops workers leaving `doing` with a dirty worktree, which removes one cause; the message remains wrong whenever a worktree is dirty.

Change, in `_run_check` in `src/chitty/run.py` only:

- Before calling `run_logged`, read `git.uncommitted_paths(branch_repo.root)`. Read it before the check runs, because a check may write files of its own. (The runner's own ticket edits are already committed: `chitty run` requires `autocommit = true`.)
- If the check exits non-zero and that list is not empty, append `; the worktree had uncommitted changes before the check: <paths>` to `detail` (each path in backticks, joined by `, `, as `_block_dirty_review` lists them), in every mode and status, and do not append the `no work yet` clause, which today is added in a separate `if`. Otherwise `detail` is unchanged.

Out of scope: committing or removing leftover changes, the timeout and command-not-found paths, passing checks, and the handoff refusal for a dirty worktree (`TASK-689`).

Test, in `tests/test_next.py` next to `test_run_check_failure_on_todo_ticket_records_error_on_branch` (no property: two fixed cases, a clean and a dirty worktree, the clean one already tested). New `test_run_check_failure_names_uncommitted_worktree_changes`: use `write_failing_checker` and `commit_ticket("Todo", "todo")`, then `git worktree add -b task-1 .worktrees/task-1 main` (the runner reuses an existing worktree for the branch), write an untracked `left.py` there, and `run_cli("run")`. Assert the ticket is `error` and its Notes contain `uncommitted changes` and `` `left.py` `` and not `no work yet`.

## Acceptance Criteria

- [ ] `test_run_check_failure_names_uncommitted_worktree_changes` passes, and fails before the change to `src/chitty/run.py`. Regression test: `test_run_check_failure_on_todo_ticket_records_error_on_branch` (its checker writes `check-args` during the check, so it still gets the `no work yet` clause)
- [ ] `make check` passes

## History

- 2026-11-24T22:21:39Z zesty-coral-newt → backlog
- 2026-11-24T22:21:39Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:33Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:57Z zesty-coral-newt: changed priority
- 2026-11-25T22:32:44Z calm-ochre-quail: changed notes
- 2026-11-25T22:35:05Z golden-coral-stoat: replaced notes; changed title, description, acceptance criteria
- 2026-11-25T22:35:05Z golden-coral-stoat backlog → planning
