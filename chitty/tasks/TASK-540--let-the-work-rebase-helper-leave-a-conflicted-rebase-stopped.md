---
title: Let the work rebase helper leave a conflicted rebase stopped
status: todo
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22, and split again after a cold read. Today `_rebase_work_worktree(worktree, task_id, main_branch) -> None` in `src/chitty/run.py` aborts a rebase that stops on a conflict and restores any saved work (rechecked on `main` 2026-11-22). The plan is that a conflict goes to an agent. This ticket changes only the helper so a caller can leave the rebase stopped; `TASK-551` extracts the runner's setup and check into a helper, and `TASK-552` uses both to start the agent on a stopped rebase.

- Add a keyword-only parameter `stop_on_conflict: bool` (no default; update the one caller in `_run_ticket_with_log` to pass `False`, so runner behaviour is unchanged by this ticket). Return `bool`: `True` when it left a rebase stopped.
- On a conflict with `stop_on_conflict=True`: if any unresolved path starts with `chitty/`, call `git.abort_rebase(worktree)`, restore saved work, and raise `ChittyError(f"rebase onto {main_branch} conflicts in ticket files: {paths}")` (decided 2026-11-22: ticket files change only on their branch, so this should not happen, and an agent cannot safely resolve it); otherwise leave the rebase stopped, do not restore saved work (it stays in `refs/chitty/stash/<ID>`), and return `True`.
- On a conflict with `stop_on_conflict=False`: abort and restore as today, return `False`. Every other path returns `False`.

Tests in `tests/test_rebase_work_worktree.py`: keep case 3 (now passing `stop_on_conflict=False`, returning `False`); add case 3b, the same conflict with `stop_on_conflict=True`: returns `True`, `git.rebase_in_progress(worktree)` is true, and `refs/chitty/stash/TASK-1` exists while `u.txt` is not in the worktree; add case 3c, a conflict in a file under `chitty/tasks/` with `stop_on_conflict=True`: raises `ChittyError` containing `conflicts in ticket files`, no rebase in progress, `u.txt` restored. Cases 3b and 3c fail before the change.

## Acceptance Criteria

- [ ] Cases 3, 3b and 3c pass, and 3b and 3c fail before the change; the runner tests in `tests/test_run_work_rebases.py` pass unchanged; `make check` passes

## History

- 2026-11-22T01:29:45Z lively-zinc-newt → planning
- 2026-11-22T02:02:17Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:40:17Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:40:17Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:42:58Z lively-zinc-newt: changed title, description, acceptance criteria
- 2026-11-22T03:42:58Z lively-zinc-newt cold-read → todo
