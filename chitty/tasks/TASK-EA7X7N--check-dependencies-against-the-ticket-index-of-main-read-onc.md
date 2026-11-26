---
title: Check dependencies against the ticket index of `main` read once per command
status: cold-read
priority: high
created: 2026-11-26
provisional: true
---

## Description

`store._dependency_is_done` (`src/chitty/store.py`) loops over every ticket file on `main` in the dependency's context and parses each file name, once for each dependency it checks. `chitty list` checks each dependency twice (`blocking_ids_for` and `list_marker`, both through `_selection_facts`), so the work grows with tickets × dependencies: on this repository on 2026-11-26 that came to 255,000 `ids.parse_filename` calls, and `_dependency_is_done` took about 5 s of `chitty list`. The files come from `Repo._main_files_for`, which reads `main`'s ticket blobs again (`git.main_files`, one `ls-tree` and one `cat-file` per context), although `Repo._ref_files()` has already read them.

Change:

- In `_dependency_is_done`, get the dependency's files on `main` from `repo._ref_ticket_files(f"refs/heads/{main}", dependency_id)`, which is indexed by ID once per `Repo`. Treat "no `main` ref in `repo._ref_files()`" as today's `main_files is None` case. Parse the returned file there as today, keeping its error text `refs/heads/<main>:<path>: <error>`. Archived or `done` counts as done, and more than one file raises `<id> is used by more than one file`. Drop the `repo.context_of` call: it only built the directory list.
- In `_ticket_action`, replace the `_main_files_for(main_branch, ())` check with the same "is there a `main` ref" check.
- Delete `git.main_files`, `Repo._main_files_for` and the `_main_files` cache (including its line in `_invalidate`).

Accepted differences: `_ref_ticket_index` looks in every `chitty/<context>/` directory, so a copy of the same ID in another context on `main` now raises `is used by more than one file`, as `_source_files` already does. `main` is read once per `Repo` (the snapshot used for source selection), not again at each dependency check. A file whose name does not parse on `main` is already reported by `Repo._collect_ticket_ids` before any dependency is checked.

Out of scope: reading ticket-branch blobs and the Git calls in source selection (separate tickets).

## Acceptance Criteria

- [ ] A test in `tests/test_list_performance.py` counts calls to `chitty.ids.parse_filename` (wrap it, as `COUNT_SCANS` wraps `store.scan`) during `chitty list` in a committed Git fixture where `TASK-2` to `TASK-n` each have `depends_on: [TASK-1]`. It asserts that the count for n = 40 is at most 8 times the count for n = 10. It fails before the change (300 and 4,800 calls today, a ratio of 16)
- [ ] `git.main_files`, `Repo._main_files_for` and `Repo._main_files` are gone. Regression tests (these already pass): `test_dependency_check_parses_only_the_dependency`, `test_malformed_other_ticket_on_main_does_not_break_a_dependency`, `test_unmerged_archive_does_not_complete_dependency` and `test_todo_dependency_must_be_done_on_main` in `tests/test_next.py`
- [ ] `make check` passes

## History

- 2026-11-26T21:56:46Z youthful-lilac-heron → cold-read
- 2026-11-26T22:00:57Z youthful-lilac-heron: changed description, acceptance criteria
