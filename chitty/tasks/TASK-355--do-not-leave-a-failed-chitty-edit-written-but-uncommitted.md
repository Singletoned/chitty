---
title: Do not leave a failed chitty edit written but uncommitted
status: cold-read
owner: open-russet-eel
created: 2026-11-16
---

## Description

Seen 2026-11-16 in `.worktrees/task-318`: `chitty edit TASK-318 --depends-on TASK-325 --depends-on TASK-326 --note ...` printed `depends_on TASK-326: no such task` and exited non-zero, but had already written the dependencies, note and history entry to the ticket file, leaving it modified and uncommitted.

Cause: `Repo.edit` in `src/chitty/store.py` writes the file (`_save`, `_write`; `_save` may also `git.move` the file when the title changes), then `_commit` runs `fix` from `src/chitty/check.py` and raises `cannot finalize task write with unresolved problems` without undoing the write. Any problem the post-write check finds but the pre-write checks miss leaves the file behind: a self-dependency, a dependency cycle, a parent cycle, and (until `TASK-356`) a dependency that exists only on another branch.

Make a refused `edit` leave the repository as it was: when `_commit` refuses, restore every file the write changed to its previous bytes and undo a title rename, before raising the same error. The error text does not change. `add` is out of scope: a new ticket cannot form a cycle, and its only post-write refusal is the cross-branch dependency that `TASK-356` removes. Other writes that call `_commit` (archive, restore, move, delete) are also out of scope.

Files: `src/chitty/store.py`; tests in a new `tests/test_property_refused_write.py`. Tests use a real git repository in a temp dir with `autocommit = true`, inheriting `RepoTestCase` from `tests/support.py`.

## Acceptance Criteria

- [ ] Hypothesis property in `tests/test_property_refused_write.py`, against one real repository holding `TASK-1` and `TASK-2` with `TASK-2` depending on `TASK-1`: draw an edit of `TASK-1` that the post-write check refuses (one of: depends on itself, depends on `TASK-2` making a cycle, parent itself), combined with optional generated `--note` text and an optional generated new title. `Repo.edit` raises `ChittyError` containing `cannot finalize task write`; afterwards `git status --porcelain` is empty and every file under `chitty/` has the same bytes as before. Use `max_examples` of at least 25 and `deadline=None`. Fails before the change. `make check` passes.

## History

- 2026-11-16T10:29:24Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:55Z intrepid-coral-raven backlog → planning
- 2026-11-16T16:56:28Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:56:39Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:56:42Z open-russet-eel: changed acceptance criteria
- 2026-11-16T16:57:31Z open-russet-eel: changed owner
- 2026-11-16T16:57:31Z open-russet-eel planning → cold-read
