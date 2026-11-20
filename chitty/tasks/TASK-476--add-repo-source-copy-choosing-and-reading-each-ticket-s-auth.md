---
title: Add `Repo.source_copy`, choosing and reading each ticket's authoritative copy
status: planning
depends_on:
  - TASK-474
parent: TASK-376
created: 2026-11-20
---

## Description

`TASK-474` adds `Repo.ticket_ids()` in `src/chitty/store.py`, listing which ticket IDs exist and caching each ref's ticket files. This ticket adds `Repo.source_copy`, which chooses each ticket's authoritative copy by `ticket_source` (`src/chitty/ticket_source.py`; the rule is in `docs/plan/ticket-state.md`, "Planning decisions", on branch `plan/ticket-state`) and reads it. Nothing uses it yet: `TASK-378` switches reads over. `TASK-477` and `TASK-478` add tests from other checkouts and for errors.

New in `src/chitty/store.py`:

- `SourceCopy`, a frozen dataclass: `ref: str | None`, the short name of the ref read (`main`, `task-5`, `origin/task-5`; never `refs/heads/...`), or `None` for this checkout's working tree; `path: Path`, relative to the repository root; `task: Task`, the parsed copy.
- `Repo.source_copy(task_id: TaskId) -> SourceCopy | None`: the copy to read, or `None` when the source has no file for the ID.

Decisions:

- Choosing the source, on the first call for an ID only (cached per ID, cleared by `_invalidate`), so a conflicted ticket fails only calls for itself: call `ticket_source` with `provisional=False` (`TASK-475` passes the real flag); `git.current_branch`; `Repo._main_branch()`; `main_tip` from `git.ref_commit(root, "refs/heads/<main>")`; `local_tips` and `remote_tips`, the ticket branches' tips (as `TASK-474` finds them) with `refs/heads/` and `refs/remotes/` stripped; `contains(a, b)` as `git.is_ancestor(root, b, a)`, `False` when `a` is `None`; and `changed_on_both(name)`, true when both `git.changed_since_split(root, ref, main, paths)` and `git.changed_since_split(root, main, ref, paths)` are true, with `ref` and `main` full refs and `paths` the union of this ID's file paths at `main`'s tip and at `ref`'s tip. With no `main` commit, `changed_on_both` returns `False` without calling Git.
- Mapping `ticket_source`'s result to a full ref: `WORKING_TREE` is this checkout; the main branch name is `refs/heads/<main>`; the ID lower-cased (`task-5`) is `refs/heads/task-5`; anything else is `refs/remotes/<result>`.
- Reading: `WORKING_TREE` reads this checkout's file, committed or not; a file deleted there but not committed is absent. A ref reads the file from `TASK-474`'s cached files for that ref; no further `git.files_at` or `git.file_at` call. No file for the ID in the source gives `None`. More than one file for the ID in the source raises the existing `<ID> is used by more than one file: <paths>` error.
- Errors from `ticket_source` and `git.changed_since_split` propagate unchanged. A copy that fails to parse raises `ChittyError` as `<short ref>:<relative path>: <error>` for a ref, and `<absolute path>: <error>` for the working tree, as `Repo._load` does.
- Outside a Git repository (`git.is_repository(root)` is false), do not call `ticket_source` or any other `chitty.git` function: read the working tree (`ref` is `None`).
- Commit `bed36801` on branch `task-378` (originally `27456731`, reverted there by `0ac2ee94`) has a first version in `_build_ticket_index`, `_source_ref` and `_changed_on_both`, choosing every source up front; reuse its code where it fits, but choose per ID on demand.

Tests: real-Git tests in a new `tests/test_source_copy.py`, set up as `TASK-474`'s `tests/test_ticket_ids.py` is, one test per placement in the criteria, all from the main checkout on `main`, calling `Repo.open(root).source_copy(...)` directly. Set `GIT_COMMITTER_DATE` where commit order matters. Before implementing, write `SourceCopy` and `source_copy` raising `NotImplementedError` and run the new tests, so each fails on its own. No property: a fixed set of placements; the generated property is `TASK-393`.

## Acceptance Criteria

- [ ] From the main checkout on `main`: a ticket edited on `task-<n>` ahead of `main` gives `ref` `task-<n>` and the branch copy, even when a later `main` commit by `GIT_COMMITTER_DATE` touches another ticket; a ticket retitled on `task-<n>` (file renamed there, `main` keeping the old name) gives the branch path; a ticket only on `origin/task-<n>`, ahead of `main`, gives `ref` `origin/task-<n>`; with local `task-<n>` behind `origin/task-<n>`, it gives `origin/task-<n>`
- [ ] From the main checkout on `main`: a ticket only on `main`, with an uncommitted edit, gives `ref` `None` and the edited task; a ticket archived on its branch but active on `main` gives the branch archive path; a ticket whose branch deletes its file gives `None`; a ticket branch fast-forward merged into `main`, followed by a `main` commit changing that ticket, gives `ref` `None` and the content committed on `main`
- [ ] With every `chitty.git` function wrapped to record calls, in a repository with `main` and ticket branches `task-1` and `task-2`, calling `source_copy` for every ID after `ticket_ids()` makes no `git.files_at` or `git.file_at` call. `make check` passes with no existing test changed (`git diff main --stat -- tests` lists only the new file)

## History

- 2026-11-20T17:43:29Z jolly-dusky-badger → planning
- 2026-11-20T17:45:24Z jolly-dusky-badger: changed description
