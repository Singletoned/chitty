---
title: Parse only the dependency's file when checking a dependency on `main`
status: doing
priority: high
created: 2026-11-19
---

## Description

`chitty list` takes about 4 s in this repository. Profiling showed 8.7 s of 10.3 s in `_dependency_is_done` (`src/chitty/store.py`): for every dependency of every `todo` ticket it fully parses (`parse`, YAML and History) every ticket file on `main`, active and archived, and only then compares IDs. 34 dependency references gave 15,259 parses. `main`'s file list is already cached per `Repo` (`_main_files_for`), so only the parsing is wasted.

Decisions:

- In `_dependency_is_done`, run `ids.parse_filename` on every path first, as today, and call `parse` only on files whose ID equals `dependency_id`.
- A malformed file name still raises `ChittyError` naming `refs/heads/<main>:<path>`. A malformed body in a file that is not the dependency no longer does: it has nothing to do with this dependency. A malformed body in the dependency's own file still raises.

Test: in `tests/test_next.py`, next to `test_todo_dependency_must_be_done_on_main` and set up the same way (a Git repo on `main`, `autocommit = false`), add ten `done` tickets and a `todo` ticket depending on one of them, commit, then call `chitty.store._dependency_is_done` once with `chitty.store.parse` wrapped (by `unittest.mock.patch` with `wraps=`) to count calls. No property: this is a call count on fixed files.

## Acceptance Criteria

- [ ] The test returns `True` and counts exactly one `parse` call; against the old `_dependency_is_done` it counts at least eleven (recorded in the notes)
- [ ] A test with a malformed body in a ticket other than the dependency on `main` still reports the dependency done; against the old code it raises `ChittyError` (recorded in the notes)
- [ ] `chitty list` in this repository is timed before and after in the notes; `make check` passes

## History

- 2026-11-19T14:29:04Z quick-ginger-lapwing → doing
