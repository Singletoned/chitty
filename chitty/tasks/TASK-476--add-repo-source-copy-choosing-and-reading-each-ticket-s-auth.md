---
title: Add `Repo.source_copy`, choosing and reading each ticket's authoritative copy
status: review
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
- Reading: `WORKING_TREE` reads this checkout's file, committed or not; a file deleted there but not committed is absent. A ref reads the file from `Repo._ticket_ref_files` (landed by `TASK-474`: full ref name to that ref's `(path, content)` pairs, filled by `ticket_ids()`; call `ticket_ids()` first if it has not run on this `Repo`); no further `git.files_at` or `git.file_at` call. The ticket branches and their tips come from `git.branch_tips`, filtered as `Repo._collect_ticket_ids` does (it already rejects a local branch named like `origin/task-5`, so local and remote names cannot collide). Find this ID's files in `_ticket_ref_files[ref]` by the same path-shape and `ids.parse_filename` rules `_collect_ticket_ids` applies. In the working tree, use `Repo._files` for the active and archive directories of every directory under `chitty/`, as `_collect_ticket_ids` does. No file for the ID in the source gives `None`. More than one file for the ID in the source raises the existing `<ID> is used by more than one file: <paths>` error.
- Errors from `ticket_source` and `git.changed_since_split` propagate unchanged. A copy that fails to parse raises `ChittyError` as `<short ref>:<relative path>: <error>` for a ref, and `<absolute path>: <error>` for the working tree, as `Repo._load` does.
- Outside a Git repository (`git.is_repository(root)` is false), do not call `ticket_source` or any other `chitty.git` function: read the working tree (`ref` is `None`).
- Commit `bed36801` on branch `task-378` (originally `27456731`, reverted there by `0ac2ee94`) has a first version in `_build_ticket_index`, `_source_ref` and `_changed_on_both`, choosing every source up front; reuse its code where it fits, but choose per ID on demand.

Recording `chitty.git` calls, wherever a criterion asks for it: wrap each public function in `chitty.git` and record only outermost calls; a call made while another wrapped `chitty.git` function is running (such as the helper `git.is_repository` calls itself) is not recorded.

Tests: real-Git tests in a new `tests/test_source_copy.py`, set up as `TASK-474`'s `tests/test_ticket_ids.py` is, one test per placement in the criteria, all from the main checkout on `main`, calling `Repo.open(root).source_copy(...)` directly. Make remote-tracking refs with `git update-ref refs/remotes/origin/task-<n> <commit>`, with no remote configured. Set `GIT_COMMITTER_DATE` where commit order matters. Compare tasks by title or status, whichever the placement changed. Before implementing, write `SourceCopy` and `source_copy` raising `NotImplementedError` and run the new tests, so each fails on its own. No property: a fixed set of placements; the generated property is `TASK-393`.

## Acceptance Criteria

- [ ] From the main checkout on `main`: a ticket edited on `task-<n>` ahead of `main` gives `ref` `task-<n>` and the branch copy, even when a `main` commit dated after the branch commit (`GIT_COMMITTER_DATE`) touches another ticket; a ticket retitled on `task-<n>` (file renamed there, `main` keeping the old name) gives the branch path; a ticket only on `origin/task-<n>`, ahead of `main`, gives `ref` `origin/task-<n>`; with local `task-<n>` behind `origin/task-<n>`, it gives `origin/task-<n>`
- [ ] From the main checkout on `main`: a ticket only on `main`, with an uncommitted edit, gives `ref` `None` and the edited task; a ticket archived on its branch but active on `main` gives the branch archive path; a ticket whose branch deletes its file gives `None`; a ticket branch fast-forward merged into `main`, followed by a `main` commit changing that ticket, gives `ref` `None` and the content committed on `main`
- [ ] With every `chitty.git` function wrapped to record outermost calls, starting after `ticket_ids()` returns, in a repository with `main` and ticket branches `task-1` and `task-2` (each with an edit ahead of `main`): `source_copy` for every ID returns the expected `ref` and path for each and makes no `git.files_at` or `git.file_at` call
- [ ] Calling `source_copy(TASK-1)` twice on one `Repo` gives the same result; after a further commit on `task-1` and `_invalidate()`, it gives the new content; a ticket only on `main` whose file is deleted in the working tree, uncommitted, gives `None`. `make check` passes with no existing test changed (`git diff main --stat -- tests` lists only the new file)

## Plan

Correct the criterion 3 fixture by committing both initial tickets on main before editing each on its branch. Verify the corrected test against the stub and implementation, then run fix, format and checks before handoff.

## Notes

Ran all 11 new placement tests against the requested source_copy stub: each failed with NotImplementedError before implementation.

Review failed (tests): The criterion 3 fixture creates both tickets only on their branches rather than editing tickets already on main. Commit both original files on main before creating the branches, then edit each on its branch and retain the call and result assertions. This is a newly found issue; there are no earlier review failures.
1: pass - make check reports OK; the four placement tests pass. Running all 11 tests with source_copy replaced by a NotImplementedError stub reports 11 errors, including all four placements.
2: pass - make check reports OK for the four placement tests; the stub run reports NotImplementedError for each.
3: fail - tests/test_source_copy.py test_no_further_ref_reads calls init_git and immediately creates each branch before writing its ticket, so it does not exercise the specified two edits of tickets present on main. The test passes in make check and fails with NotImplementedError under the stub, but the required fixture is missing.
4: pass - make check reports 825 tests OK; invalidation and deletion tests fail with NotImplementedError under the stub. git diff main --stat -- tests lists only tests/test_source_copy.py.

Corrected criterion 3 fixture: both original tickets are committed on main before their branches edit them. The corrected test fails with NotImplementedError when source_copy is patched to the requested stub and passes with the implementation.

## Summary

Implemented lazy per-ticket source selection and reading with cached ref files and invalidation. Corrected the criterion 3 fixture after review so both branch edits start from tickets committed on main. The corrected test fails against the stub and passes with the implementation; make check passes 825 tests, and only the new test file differs from main. TASK-477 and TASK-478 cover other checkouts and errors; TASK-378 integrates reads.

## History

- 2026-11-20T17:43:29Z jolly-dusky-badger → planning
- 2026-11-20T17:45:24Z jolly-dusky-badger: changed description
- 2026-11-20T19:05:55Z jolly-dusky-badger: changed description
- 2026-11-20T19:47:08Z jolly-dusky-badger: changed description
- 2026-11-20T19:47:08Z jolly-dusky-badger planning → cold-read
- 2026-11-20T19:49:07Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T19:49:07Z jolly-dusky-badger cold-read → todo
- 2026-11-20T19:49:15Z daring-coral-adder todo → doing
- 2026-11-20T19:50:34Z daring-coral-adder: wrote the plan
- 2026-11-20T19:51:40Z daring-coral-adder: changed notes
- 2026-11-20T19:54:45Z daring-coral-adder: changed summary
- 2026-11-20T19:54:48Z daring-coral-adder doing → review
- 2026-11-20T19:57:35Z mellow-quartz-newt: changed acceptance criteria, notes
- 2026-11-20T19:57:35Z mellow-quartz-newt review → doing
- 2026-11-20T19:59:01Z rosy-white-quail: wrote the plan
- 2026-11-20T19:59:22Z rosy-white-quail: changed notes
- 2026-11-20T20:00:24Z rosy-white-quail: changed summary
- 2026-11-20T20:00:27Z rosy-white-quail doing → review
