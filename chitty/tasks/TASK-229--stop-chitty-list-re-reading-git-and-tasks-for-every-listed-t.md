---
title: Stop `chitty list` re-reading git and tasks for every listed task
status: backlog
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
- Cache on the `Repo` instance, which lives for one CLI command or one MCP tool call (`src/chitty/mcp.py:57` opens a new one each call). Cache the result of `_tasks_in_location` per (context, archived), `git.current_branch`, `git.dirty_paths` per directory, `_main_branch`, and `git.main_files` per (branch, directories). Follow the existing `_historical_files` pattern (`store.py:202`, `store.py:283`).
- Clear every one of these caches whenever the `Repo` writes a task file or commits. A read after a write on the same `Repo` must see the write.
- Cache `config.git_common_dir` per root with `functools.cache`. It cannot change for a path. Do not cache `locks.locked_ids`, because locks change while a run is going.
- Keep `cli.py` and `mcp.py` unchanged apart from call sites. The behaviour lives in `store.py`.

Out of scope: caching across commands, running git calls in parallel, and the per-process cost of starting git.

## Acceptance Criteria

- [ ] A new test in `tests/test_list_performance.py` builds a git repo with a `main` branch and N `todo` tasks, each depending on a task already `done`, and runs `chitty list` with `GIT_TRACE` set to a file. The number of git processes recorded is the same for N=2 and N=10. Record that this test failed before the fix.
- [ ] A test shows that, on one `Repo`, `tasks()` and `find()` return a task's new status after that `Repo` edits it.
- [ ] `make check` passes.

## History

- 2026-11-08T10:31:35Z calm-eel → backlog
