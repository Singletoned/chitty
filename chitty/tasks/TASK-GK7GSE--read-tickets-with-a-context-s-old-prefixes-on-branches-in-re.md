---
title: Read tickets with a context's old prefixes on branches, in references and in branch cleanup
status: cold-read
depends_on:
  - TASK-MQ87S9
parent: TASK-W74AVC
created: 2026-11-26
provisional: true
---

## Description

### Why

Part of TASK-W74AVC. After a person changes a context's `prefix` and lists the old one in `old_prefixes` (TASK-MQ87S9), old tickets must keep working everywhere Chitty matches IDs by prefix.

### Change

Where these build a set of prefixes from `context.prefix`, add each context's `old_prefixes`:

- `Repo.context_of` (`src/chitty/store.py`): the fallback that matches `context.prefix == task_id.prefix`.
- The set used to find ticket branches (`prefixes = {context.prefix for context in self.contexts()}`, just before the `ref != main_ref` check), so a `task-<n>` branch for an old ticket is still read.
- `Repo.referenced_tasks` (the listing after `chitty edit -s todo`).
- `_remove_merged_branches` in `src/chitty/run.py`.

`scan`'s prefix check needs no change: every caller passes `allow_any_prefix=True`. `import_backlog` keeps using the current `prefix` for new imports.

### Out of scope

Numbering (sibling ticket); the setting itself (TASK-MQ87S9).

## Acceptance Criteria

- [ ] In a new `tests/test_old_prefixes.py` (`CliTestCase` with Git, as `tests/test_landing.py` sets it up), with tickets `TASK-1` and `TASK-2` committed on `main`, then the `tasks` context changed in `chitty.toml` to `prefix = "TK"` and `old_prefixes = ["TASK"]` and committed: (a) an edit of `TASK-2` committed on branch `task-2` is what `chitty show TASK-2` on `main` reads, as for a current-prefix ticket; (b) a `planning` ticket whose Description mentions `TASK-1`, moved with `chitty edit <ID> -s todo`, lists `TASK-1` as a referenced ticket. Fails without the change. Regression tests: `chitty show TASK-1` and `chitty edit <ID> --depends-on TASK-1` work.
- [ ] In `tests/test_run_removes_merged_branches.py`, extend the existing test so a merged `task-<n>` branch whose ticket uses an old prefix is removed like one using the current prefix. Fails without the change. `make check` passes.

## History

- 2026-11-26T17:52:20Z calm-ochre-quail → cold-read
