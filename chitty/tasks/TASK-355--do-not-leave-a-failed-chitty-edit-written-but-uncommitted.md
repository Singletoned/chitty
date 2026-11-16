---
title: Do not leave a failed chitty edit written but uncommitted
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16 in `.worktrees/task-318`: `chitty edit TASK-318 --depends-on TASK-325 --depends-on TASK-326 --note ...` printed `depends_on TASK-326: no such task` and exited non-zero, but had already written the dependencies, note and history entry to the ticket file, leaving it modified and uncommitted.

Cause: `Repo.edit` and `Repo.add` in `src/chitty/store.py` write the file (`_save`, `_write`; `_save` may also `git.move` the file when the title changes), then `_commit` runs `fix` from `src/chitty/check.py` and raises `cannot finalize task write with unresolved problems` without undoing the write. Any problem the post-write check finds but the pre-write checks miss leaves the file behind: a self-dependency, a dependency cycle, a parent cycle, and (until `TASK-356`) a dependency that exists only on another branch.

Make a refused `add` or `edit` leave the repository as it was: when `_commit` refuses, restore every file the write changed to its previous bytes, undo a title rename, and remove a file `add` created, before raising the same error. The error text does not change. Other writes that call `_commit` (archive, restore, move, delete) are out of scope.

Files: `src/chitty/store.py`; tests in a new `tests/test_property_refused_write.py`. Tests use a real git repository in a temp dir with `autocommit = true`, inheriting `RepoTestCase` from `tests/support.py`.

## Acceptance Criteria

- [ ] Hypothesis property in `tests/test_property_refused_write.py`, against one real repository holding `TASK-1` and `TASK-2` with `TASK-2` depending on `TASK-1`: draw an edit of `TASK-1` that the post-write check refuses (one of: depends on itself, depends on `TASK-2` making a cycle, parent itself), combined with optional generated `--note` text and an optional generated new title. `Repo.edit` raises `ChittyError` containing `cannot finalize task write`; afterwards `git status --porcelain` is empty and every file under `chitty/` has the same bytes as before. Use `max_examples` of at least 25 and `deadline=None`. Fails before the change.
- [ ] A real-file test: `chitty add` with `--depends-on` that the post-write check refuses (for example a dependency cycle through `--parent` is not possible on add, so use `--parent` and `--depends-on` naming tickets that form a dependency cycle with the new one, or another add-only refusal the worker finds and notes) exits non-zero, leaves no new file and `git status --porcelain` empty. If no add input reaches the post-write refusal, say so in a note with the evidence and drop this criterion by returning the ticket to planning. Fails before the change. `make check` passes.

## History

- 2026-11-16T10:29:24Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:55Z intrepid-coral-raven backlog → planning
- 2026-11-16T16:56:28Z open-russet-eel: changed description, acceptance criteria
