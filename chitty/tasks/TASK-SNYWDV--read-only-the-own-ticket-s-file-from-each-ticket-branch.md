---
title: Read only the own ticket's file from each ticket branch
status: todo
priority: high
created: 2026-11-26
provisional: true
---

## Description

`Repo._ref_files` (`src/chitty/store.py`) calls `git.files_at` for `main` and for each `task-<n>` branch (local or remote-tracking). Each call runs `ls-tree` and then reads every blob under `chitty/` with its own `git cat-file --batch`. On this repository that is 14 refs × about 770 files, 1.3 s of `chitty list` (2026-11-26). Every reader of a ticket branch's files uses only that branch's own ticket: `_collect_ticket_ids` and `discovered_contexts` filter to it, and `_ref_ticket_files(ref, id)` is only called with the branch's own ID (`_source_files`, `_choose_source`, `_require_current_version`).

Change: keep one `ls-tree` per ref, which supplies the file names. For a ticket branch, read the contents only of the files that `_ref_ticket_index` would index under that branch's own ID. Use the same path-shape and name rule (`chitty/<context>/<file>` or `chitty/<context>/archive/<file>`), factored into one helper that both use. The helper skips hidden entries (`ids.is_hidden_entry`, such as `.gitkeep`) before parsing, as `_collect_ticket_ids` does today, so a hidden file on `main` still does not raise. Read the blobs of every ref, `main` included, in one `git cat-file --batch` run. In `src/chitty/git.py`, replace `files_at` (its only caller is `_ref_files`) with a function returning `(path, object_id)` entries for one ref, and read the chosen objects with the existing `_read_blobs`. Keep its error messages. File names that do not parse are still skipped on ticket branches, and on `main` they still raise in `_collect_ticket_ids`.

The `_ref_files` mapping keeps its shape (ref to `(path, content)` pairs). On ticket branches it now holds only the own ticket's files; `_collect_ticket_ids` and `discovered_contexts` already ignore the rest.

Out of scope: the per-branch ancestry and diff calls in `_choose_source` (TASK-604).

## Acceptance Criteria

- [ ] A test in `tests/test_list_performance.py` counts `trace: built-in: git cat-file` lines under `GIT_TRACE` for `chitty list` in a committed fixture with 1 and with 3 unmerged `task-<n>` branches (built like `TestScanCounts._fixture`), each changing its own ticket. It asserts the counts are equal, and it fails before the change (2 and 4 runs today)
- [ ] A test commits, on branch `task-2` only, a ticket file for `TASK-1` that is not valid UTF-8. It asserts that `Repo.open(root).lookup` of `TASK-1` and of `TASK-2` both succeed, `TASK-2` with the title of its branch copy. It fails before the change (`Git file is not UTF-8`)
- [ ] Regression tests: `TestScanCounts` and `test_ref_files_with_unparseable_names_are_skipped` in `tests/test_list_performance.py`, and `tests/test_property_hidden_entries.py`
- [ ] Regression tests: `TestScanCounts` and `test_ref_files_with_unparseable_names_are_skipped` in `tests/test_list_performance.py`

## History

- 2026-11-26T21:57:05Z youthful-lilac-heron → cold-read
- 2026-11-26T22:00:23Z youthful-lilac-heron: changed description, acceptance criteria
- 2026-11-26T22:03:06Z youthful-lilac-heron: changed description, acceptance criteria
- 2026-11-26T22:03:06Z youthful-lilac-heron cold-read → todo
