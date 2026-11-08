---
title: Stop `chitty list` re-reading git and tasks for every listed task
status: doing
labels:
  - bug
priority: medium
created: 2026-11-08
---

## Description

`chitty list` takes about 4s on this repo (235 task files). It calls `skip_reason` (`src/chitty/store.py:1220`) once for each listed task, and each call repeats work whose inputs do not change during one command:

- `locks.is_locked` runs `git rev-parse --git-common-dir` through `config.git_common_dir` (`src/chitty/config.py:314`) each time.
- For each dependency, `Repo.find` (`store.py:290`) calls `_tasks_in_location` (`store.py:249`) twice. Each call reloads every local task file, re-parses the YAML of every historical file (the git read is cached in `_history()`, the parse is not), and runs `git.dirty_paths` and `git.current_branch` again.
- `_dependency_is_done` (`store.py:1313`) calls `git.main_files` (`src/chitty/git.py:96`) each time. That re-runs `is_repository`, `has_local_branch`, two `ls-tree` calls and a `cat-file` batch, and `_main_branch` re-runs `is_linked_worktree`.

One `chitty list` spawns 92 git subprocesses and 4,307 YAML parses. A profile showed 9.2s of 10.8s inside `skip_reason`.

Decisions:
- Cache on the `Repo` instance, which lives for one CLI command or one MCP tool call (`src/chitty/mcp.py:57` opens a new one each call). Cache the result of `_tasks_in_location` per (context, archived), `git.current_branch`, `git.dirty_paths` per directory, `_main_branch`, and `git.main_files` per (branch, directories). Keep the accessors private `Repo` methods, as `_history()` (`store.py:283`) is. `_tasks_in_location` returns a new list each call.
- Add `Repo._invalidate()`, which clears every one of these caches and `_historical_files` (nothing clears that today). Call it after each `Repo` write: `_write`, each `stored.path.unlink()` and `stored.path.rename()`, `git.move` in `_save`, and the end of `_commit`. `check.fix` and the formatter write outside `Repo` but run only from `_commit`, so the call at its end covers them. A read after a write on the same `Repo` must see the write.
- Cache `config.git_common_dir` per root with `functools.cache`. It cannot change for a path. Do not cache `locks.locked_ids`, because locks change while a run is going.
- Keep `cli.py` and `mcp.py` unchanged apart from call sites. The behaviour lives in `store.py`.

Out of scope: caching across commands, files changed by other processes while one `Repo` is open, running git calls in parallel, and the per-process cost of starting git.

## Acceptance Criteria

- [x] A new test in `tests/test_list_performance.py` builds a git repo with a `main` branch and N `todo` tasks, each depending on a task already `done` (set `review = false` in `chitty.toml` and `CHITTY_ACTOR` to set that up). It runs `chitty list` in a subprocess (`python -c 'from chitty.cli import main; main()' list`; there is no `__main__.py`) with `GIT_TRACE` set to a file, so the process-wide `git_common_dir` cache starts empty each run. The number of `trace: built-in: git` lines is the same for N=2 and N=10. Record that this test failed before the fix.
- [x] A regression test shows that, on one `Repo`, `tasks()` and `find()` return a task's new status after that `Repo` edits it. It passes before the fix too; it guards the cache clearing.
- [x] `make check` passes.

## Plan

1. Inspect the existing Repo, git, config, and list tests to map all cache inputs and write paths.
2. Add Repo-scoped private accessors and invalidation covering task-location data, git-derived values, historical files, and main files; cache git_common_dir per root.
3. Add the subprocess git-trace performance regression and the same-Repo write/read cache invalidation regression, first running the performance test against the current code.
4. Run formatting and make check, then verify and hand off the ticket.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-229/1`): the implementation passed `make check`; the criterion 1 test failed first with `120 != 32`; `chitty list` dropped from about 4s to 1.4s. Outcomes:
1. An in-process `CliRunner` count differs by one between runs, because `git_common_dir` is cached per process. Fixed: criterion 1 runs `chitty list` in a subprocess.
2. The criterion 1 setup is non-obvious. Fixed: it names `review = false` and `CHITTY_ACTOR`.
3. Criterion 2 passes without the fix. Fixed: it is labelled a regression guard.
4. The write sites are spread out, and `_historical_files` is never cleared, so pointing at the existing pattern does not cover clearing. Fixed: the Decisions name `Repo._invalidate()`, every call site, and `_historical_files`.
5. Where the accessors live, and whether `_tasks_in_location` returns a copy. Fixed: private `Repo` methods, and a new list each call.
6. Files changed by another process during one `Repo`. Rejected: a `Repo` lasts one command or MCP call. Now named out of scope.
7. A process-wide `git_common_dir` cache goes stale if a git dir moves under the same path. Rejected: a checkout's git dir does not move during one process.
8. The 92-subprocess and 4,307-parse figures were unchecked by the reader. Rejected: the planner measured them with `cProfile` on this repo.

Verified the subprocess GIT_TRACE regression: before the fix, the new test failed with 30 git calls for N=2 versus 118 for N=10; after the fix it passes with equal counts. The same-Repo edit regression passes, and make check passes.

## History

- 2026-11-08T10:31:35Z calm-eel → backlog
- 2026-11-08T10:37:06Z calm-eel: changed description, acceptance criteria, notes
- 2026-11-08T10:37:06Z calm-eel backlog → todo
- 2026-11-08T11:36:53Z able-dormouse todo → doing
- 2026-11-08T11:37:59Z able-dormouse: wrote the plan
- 2026-11-08T11:42:57Z able-dormouse: changed notes; ticked acceptance criteria
