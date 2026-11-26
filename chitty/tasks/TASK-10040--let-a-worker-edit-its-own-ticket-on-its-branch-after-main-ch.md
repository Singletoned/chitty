---
title: Let a worker edit its own ticket on its branch after `main` changed it, with a warning to merge
status: todo
depends_on:
  - TASK-602
created: 2026-11-26
---

## Description

Rule (the person, 2026-11-26, in `docs/plan/principles.md`): work off `main` assumes it runs in isolation, writes its own branch's copy, and warns instead of refusing. A worker whose ticket changed on `main` is told to merge or rebase now: if the merge is trivial it might as well happen, and if there are conflicts it is better to get them over with.

Today a worker on its own ticket branch (`task-6` for `TASK-6`) is refused once `main` has changed that ticket since the branch split. `chitty edit TASK-6 ...` gives `TASK-6's latest committed version is on branch main; run Chitty in worktree <main checkout>` (`_require_current_version` in `src/chitty/store.py`), so workers cannot set `review` (seen in TASK-495 and TASK-492).

Change, in `src/chitty/store.py`, building on TASK-602 (`_planning_conflict_warnings`, `branch_change_warning` and the warnings in `Change.warnings`):

- Add `own_ticket_branch(task_id) -> str | None`, which returns the current branch when it equals `str(task_id).lower()` and `None` otherwise. Leave `planning_branch()` as it is (`test_branch_selection` expects `None` for `task-1`).
- When `own_ticket_branch(task_id)` is set, `edit_current`, `archive_current` and `find_for_show` treat that ticket as they treat a `plan/` branch: they use its working-tree copy (through `_branch_task`), with `_planning_conflict_warnings`. Other tickets on a ticket branch, and every other branch, are unchanged. This supersedes TASK-10027's exclusion of ticket branches, for the branch's own ticket only.
- `_require_current_version` and `Repo.edit` stay as they are, so the runner and `--human` edits are unchanged.

A claim or other change made on `main` stays invisible on the branch until it is merged in. The runner's merge of `main` before review is unchanged, and that is where any conflict comes up. The warning text is TASK-602's: `<ID> also changed on refs/heads/main (status there: <status>); merge or rebase it now and resolve any conflict`.

Tests, in `tests/test_own_worktree_writes.py`:

- Rewrite `test_cli_write_then_refuse_after_merge_and_main_change` as `test_cli_write_warns_after_main_change`, keeping its first edit and `merge --ff-only task-6`. After `change_main()`, `chitty edit TASK-6 --note x` from the worktree exits 0, commits on `task-6`, and its output contains `branch_change_warning(TaskId("TASK", 6), "refs/heads/main", "todo")`. Then `chitty show TASK-6` in the worktree shows the branch's copy (`Description.`, not `Main change.`). Before the change, the edit is refused.
- Regression tests: with `main` unchanged, the same edit commits on `task-6` and prints no `also changed on`. `test_guard_refuses_changed_main` and the other `_require_current_version` tests still pass.

Out of scope: rebasing or merging automatically, the runner, other tickets on a ticket branch, and MCP warnings (TASK-10034).

## Acceptance Criteria

- [ ] The rewritten `test_cli_write_warns_after_main_change` passes and fails before the change (record it in a note); the regression tests pass
- [ ] `make check` passes

## History

- 2026-11-26T18:00:46Z brisk-bronze-adder → planning
- 2026-11-26T18:01:32Z brisk-bronze-adder planning → cold-read
- 2026-11-26T18:03:58Z brisk-bronze-adder cold-read → planning
- 2026-11-26T18:04:00Z brisk-bronze-adder: changed description
- 2026-11-26T18:04:00Z brisk-bronze-adder planning → todo
