---
title: Commit or restore a ticket file when a Chitty write fails after writing it
status: planning
labels:
  - bug
parent: TASK-376
created: 2026-11-18
---

## Description

A Chitty write that fails after writing files leaves them changed and uncommitted. Seen repeatedly: `TASK-366`'s and `TASK-359`'s worktrees, and on 2026-11-18 `chitty archive TASK-359` (in its worktree) and `chitty archive TASK-372` (on `main`) both moved the file, then failed with `used by more than one file` and left the active file deleted and the archive file untracked (details in the notes). That trigger comes from the history-based read, which `TASK-378` replaces, but the missing restore is general: only `Repo.edit` in `src/chitty/store.py` snapshots ticket files and the index (`_task_file_bytes`, `_restore_task_files`), and only for errors whose message contains `cannot finalize task write`, so it does not restore after `autocommit failed` either (a cold read reproduced every command below, `edit` included, leaving files behind with a failing pre-commit hook). `add`, `archive`, `archive_done`, `restore`, `move`, `renumber` and delete-mode archiving restore nothing.

Decisions:

- One helper in `src/chitty/store.py`, a context manager `Repo._all_or_nothing()`, used by every public ticket write (`add`, `edit`, `archive`, `archive_done`, `restore`, `move`, `renumber`, and `renumber_provisional` once `TASK-391` adds it): before the first file write it snapshots the ticket files (`_task_file_bytes`) and the index bytes; on any exception it restores both, calls `self._invalidate()` and re-raises the original exception unchanged. `Repo.edit` uses it in place of its message test.
- `_prepare_write()` (setup upgrade) runs before the snapshot and is not undone, as today.
- Out of scope: the history-read trigger itself (`TASK-378`).

Tests: real-Git tests in a new `tests/test_failed_writes_restore.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`, a configured user, `autocommit = true`, a current setup (`chitty_version` equal to `CHITTY_VERSION`, so `_prepare_write` writes nothing), and a `.git/hooks/pre-commit` that exits 1 to make every autocommit fail after the files are written (as `tests/test_autocommit.py` does). No property: a fixed set of commands, each listed in the criteria and tested.

## Acceptance Criteria

- [ ] With the failing hook, each of `chitty add`, `chitty edit --note`, `chitty archive <ID>`, `chitty archive` (no ID), `chitty move <ID> human`, `chitty renumber <PATH>` (a duplicate made with `git mv`), and a direct `Repo.restore(<ID>)` call (there is no CLI command) fails with the autocommit error, and afterwards `git status --porcelain` and every ticket file's bytes equal what they were before; each fails before the change
- [ ] The same holds with `archive = "delete"` for `chitty archive <ID>`; a later run of each command without the hook succeeds; `make check` passes

## Notes

Reproduced 2026-11-18 in `.worktrees/task-359` (branch `task-359`, clean worktree, ticket committed there and also present on `main`): `chitty edit TASK-359 --note ...` succeeded, then `chitty archive TASK-359` failed with `TASK-359 is used by more than one file: .../chitty/tasks/TASK-359--....md, .../chitty/tasks/archive/TASK-359--....md`, leaving the active file deleted and the archive file untracked, uncommitted. The same command on `main` for `TASK-366` (also on branch `task-366`) succeeded. Undone by hand with `git restore` and `rm`.

Also on `main` 2026-11-18: `chitty edit TASK-372 --note ...` then `chitty archive TASK-372` (status `planning`, no local or remote `task-372` branch; the branch existed earlier and was removed after landing) failed the same way and left the move uncommitted. `TASK-366` archived fine on `main` minutes earlier. Repro candidate: a ticket whose active path appears in the history of a deleted branch or of `main` itself.

## History

- 2026-11-18T16:20:21Z lively-quartz-crane → backlog
- 2026-11-18T16:25:57Z lively-quartz-crane: changed notes
- 2026-11-18T16:26:22Z lively-quartz-crane: changed notes
- 2026-11-18T17:56:41Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T17:56:41Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:43Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:56:59Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:59:25Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:59:25Z lively-quartz-crane cold-read → planning
