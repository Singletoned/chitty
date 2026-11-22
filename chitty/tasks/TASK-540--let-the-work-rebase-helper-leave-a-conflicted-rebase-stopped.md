---
title: Let the work rebase helper leave a conflicted rebase stopped
status: doing
depends_on:
  - TASK-370
  - TASK-546
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-370` on 2026-11-22, and split again after a cold read. Today `_rebase_work_worktree(worktree, task_id, main_branch) -> None` in `src/chitty/run.py` aborts a rebase that stops on a conflict and restores any saved work (rechecked on `main` 2026-11-22). The plan is that a conflict goes to an agent. This ticket changes only the helper so a caller can leave the rebase stopped; `TASK-551` extracts the runner's setup and check into a helper, and `TASK-552` uses both to start the agent on a stopped rebase.

- Add a keyword-only parameter `stop_on_conflict: bool` (no default; update the one caller in `_run_ticket_with_log` to pass `False`, so runner behaviour is unchanged by this ticket). Return `bool`: `True` when it left a rebase stopped.
- On a conflict with `stop_on_conflict=True`: if any unresolved path starts with `f"{BACKLOG_DIR}/"` (`BACKLOG_DIR` is `chitty`, in `src/chitty/config.py`), call `git.abort_rebase(worktree)`, restore saved work, and raise `ChittyError(f"rebase onto {main_branch} conflicts in ticket files: {paths}")` (decided 2026-11-22: ticket files change only on their branch, so this should not happen, and an agent cannot safely resolve it); otherwise leave the rebase stopped, do not restore saved work (it stays in `refs/chitty/stash/<ID>`), and return `True`.
- On a conflict with `stop_on_conflict=False`: abort and restore as today, return `False`. Every other non-raising path returns `False`.

Tests in `tests/test_rebase_work_worktree.py`: change its `rebase()` helper (near line 45) to pass `stop_on_conflict=False`, so the existing cases keep their behaviour (do not add a default to the parameter); keep case 3, now also asserting it returns `False`; add case 3b, the same conflict with `stop_on_conflict=True`: returns `True`, `git.rebase_in_progress(worktree)` is true, and `refs/chitty/stash/TASK-1` exists while `u.txt` is not in the worktree; add case 3c with `stop_on_conflict=True`: in a variant of the fixture, also commit `chitty/tasks/T.md` in the initial commit and have the branch and `main` each change it, so the rebase conflicts on that path; the call raises `ChittyError` containing `conflicts in ticket files`, no rebase in progress, `u.txt` restored. add case 3d: a clean rebase with `stop_on_conflict=True` returns `False`, no rebase is in progress, and saved work is restored. Cases 3b and 3c must fail on their behaviour assertions (shown by running them against the old helper with the keyword ignored), not only on the new keyword.

## Acceptance Criteria

- [ ] Cases 3, 3b, 3c and 3d pass; 3b and 3c fail on their behaviour assertions against the old helper; the runner tests in `tests/test_run_work_rebases.py` pass unchanged; `make check` passes

## Plan

Add conflict and clean-rebase regression cases, verify old behavior fails, then implement the keyword-only switch and run checks.

## Notes

Regression cases 3b and 3c fail against the old helper with the keyword accepted and ignored: respectively None is not true and ChittyError is not raised.

## Summary

Implemented stopped conflict handling and regression coverage. Old helper failed cases 3b and 3c on behavior assertions; make check passed (1099 tests).

## History

- 2026-11-22T01:29:45Z lively-zinc-newt → planning
- 2026-11-22T02:02:17Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:40:17Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:40:17Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:42:58Z lively-zinc-newt: changed title, description, acceptance criteria
- 2026-11-22T03:42:58Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:43:12Z lively-zinc-newt todo → cold-read
- 2026-11-22T03:45:00Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:45:00Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:49:54Z witty-lilac-raven todo → doing
- 2026-11-22T03:52:03Z witty-lilac-raven: wrote the plan
- 2026-11-22T03:52:35Z witty-lilac-raven: changed notes
- 2026-11-22T03:55:10Z witty-lilac-raven: changed summary
