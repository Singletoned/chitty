---
title: Read tickets with a context's old prefixes on branches, in references and in branch cleanup
status: doing
depends_on:
  - TASK-10048
parent: TASK-10053
created: 2026-11-26
moved_from: TASK-GK7GSE
---

## Description

### Why

Part of TASK-10053. After a person changes a context's `prefix` and lists the old one in `old_prefixes` (TASK-10048), old tickets must keep working everywhere Chitty matches IDs by prefix.

### Change

Add a property `Context.prefixes` (`(prefix, *old_prefixes)`) in `src/chitty/store.py`, and use it where these build a set of prefixes from `context.prefix` (in `run.py`, iterate `main_repo.contexts()`):

- `Repo.context_of` (`src/chitty/store.py`): the fallback that matches `context.prefix == task_id.prefix`.
- The set used to find ticket branches (`prefixes = {context.prefix for context in self.contexts()}`, just before the `ref != main_ref` check), so a `task-<n>` branch for an old ticket is still read.
- `Repo.referenced_tasks` (the listing after `chitty edit -s todo`).
- `_remove_merged_branches` in `src/chitty/run.py`.

`scan`'s prefix check needs no change: every caller passes `allow_any_prefix=True`. `import_backlog` keeps using the current `prefix` for new imports.

### Out of scope

Numbering (sibling ticket); the setting itself (TASK-10048).

## Acceptance Criteria

- [ ] In a new `tests/test_old_prefixes.py`, a bare `CliTestCase` copies the Git setup from `LandingTestCase.setUp` (`tests/test_landing.py`) without inheriting it. With tickets `TASK-1` and `TASK-2` committed on `main`, then the `tasks` context changed in `chitty.toml` to `prefix = "TK"` and `old_prefixes = ["TASK"]` and committed: (a) an edit of `TASK-2` committed on branch `task-2` (in a worktree) is what `chitty show TASK-2` on `main` reads, as for a current-prefix ticket; (b) a `planning` ticket created by the test's own actor, whose Description mentions `TASK-1`, moved with `chitty edit <ID> -s todo`, lists `TASK-1` as a referenced ticket. Fails without the change. Regression tests: `chitty show TASK-1` and `chitty edit <ID> --depends-on TASK-1` work.
- [ ] In `tests/test_run_removes_merged_branches.py`, extend `test_removes_done_and_unknown_branches` (or add a sibling using its setup): after switching to `prefix = "TK"` with `old_prefixes = ["TASK"]` committed on `main`, a merged `task-<n>` branch for a done old-prefix ticket is removed like one using the current prefix. Fails without the change. `make check` passes.

## History

- 2026-11-26T17:52:20Z calm-ochre-quail → cold-read
- 2026-11-26T17:53:36Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T17:53:36Z calm-ochre-quail cold-read → todo
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-GK7GSE
- 2026-11-27T01:21:14Z nimble-pearl-quail todo → doing
