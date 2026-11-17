---
title: Choose one version of a ticket across its active and archive directories
status: doing
labels:
  - bug
  - escape
priority: high
created: 2026-11-17
---

## Description

Seen twice on 2026-11-17. On `main`, `chitty archive TASK-326` (and `TASK-356`) moved the file to `chitty/tasks/archive/`, then failed with `TASK-326 is used by more than one file: chitty/tasks/TASK-326--....md, chitty/tasks/archive/TASK-326--....md` and committed nothing, leaving `main` dirty. That dirty state, for `TASK-342`, is what made `chitty run` fail to land `TASK-326`. In the `task-364` worktree, which was made before `TASK-356` was archived on `main`, every `chitty edit` failed with `TASK-356 is used by more than one file`, naming the worktree's active file and `main`'s archived one.

Reproduced 2026-11-17 in a fresh repository with `autocommit = true` and no other branch: add `TASK-1`, add `TASK-2` with `--parent TASK-1`, set `TASK-1` done, then `chitty archive TASK-1` fails the same way and leaves ` D chitty/tasks/TASK-1--....md` and `?? chitty/tasks/archive/`. Archiving a ticket nothing references succeeds. Since `TASK-356`, `check` resolves `parent` and `depends_on` through `Repo.lookup` while finalizing the write, and `lookup` sees `HEAD`'s committed active copy beside the dirty archived file.

Cause: `_tasks_in_location` in `src/chitty/store.py` picks one version per ticket for the active directory and, separately, for the archive directory, each from the current checkout's files and every branch's committed versions (`git.historical_files`). `lookup` then refuses any ticket found in both. After an archive, other branches still have the active file, and branches made earlier still have it locally.

Decisions:

- Choose one version per ticket across both directories of a context, with the rule `_tasks_in_location` already uses, as a pure function in `src/chitty/store.py`:
  - `Version`: a frozen dataclass of `stored: StoredTask` (its `archived` says which directory), `local: bool` (a file in the current checkout), `dirty: bool` (local and changed or untracked in Git), `branch: str | None` (for a historical version, the ref it came from), `committed_at: int | None` (for a historical version).
  - The candidates for a ticket are its local files in both directories, plus the newest historical version of each of its paths, except a historical version on the current branch of a path that is also a local file (the local file stands for it). A historical version of a path the current checkout has deleted stays a candidate.
  - `choose_version(versions: Sequence[Version], current_branch: str | None) -> Version`. More than one local version raises `ChittyError` with the existing `<ID> is used by more than one file: <paths>` text: that is a real duplicate in this checkout. Otherwise a dirty local version wins, whatever its directory. Otherwise, when the newest historical version (greatest `committed_at`) is on a branch other than `current_branch`, it wins. Otherwise the local version wins, or the newest historical version when there is no local one. Ties on `committed_at` prefer `current_branch`, then the smaller branch name. With `current_branch` `None` (detached), every historical version counts as another branch's.
  - Consequence, accepted: if another branch commits to a ticket's active file after `main` archived it, `main` sees that branch's active version, and a write on `main` refuses as it does for any ticket a newer branch has changed.
- `tasks`, `all_tasks` and `lookup` use it, so a ticket appears once, as active or archived by the chosen version. The `which` filter in `tasks` applies after choosing. Keep the per-location cache, or cache per context.
- Leave the `used by more than one file` special cases in `_ticket_action` and `_dependency_is_done` as they are.
- No change to `git.historical_files`, or to how a ticket the current branch has changed beats `main` (`TASK-356`).

Tests: Hypothesis properties for `choose_version` in a new `tests/test_property_choose_version.py`, over lists of versions with random branches from a small set plus `None` for the current branch, random times with frequent ties, and either directory: with at most one local version, the result is one of the inputs, a dirty local version wins, shuffling the input does not change the result, and adding a historical version older than every other version does not change the result; with two or more local versions, it raises. Real-Git tests in a new `tests/test_archive_across_branches.py`, in the style of `tests/test_check_cross_branch_references.py`: with `autocommit = true`, the reproduction above (`chitty archive TASK-1` while `TASK-2` has `parent: TASK-1`) succeeds, commits, and leaves `git status` clean; and in a worktree made before `main` archived `TASK-2`, `chitty edit TASK-1 --depends-on TASK-2` succeeds and `chitty show TASK-2 --json` reports it archived. Both fail before the change. Add `Version` and `choose_version` first, raising `NotImplementedError`, so the property tests fail on behaviour rather than import.

Out of scope: a failed write leaving its file uncommitted (a separate ticket), and picking versions by ref tip instead of newest commit (`TASK-366`).

## Acceptance Criteria

- [ ] Hypothesis properties in `tests/test_property_choose_version.py` assert `choose_version` returns an input, a dirty local version wins in either directory, order and ties do not matter, an older historical version changes nothing, and two local versions raise; the tests fail with the stub
- [ ] The two real-Git tests in Tests pass (archive of a referenced ticket commits and leaves `git status` clean; an older worktree can add a dependency on an archived ticket and sees it archived), and both fail before the change
- [ ] `make check` passes

## Notes

Also seen 2026-11-17: in the `task-364` worktree, which branched before `TASK-356` was archived on `main`, `chitty edit TASK-364 --note ...` failed with `TASK-356 is used by more than one file` (the local active file and `main`'s archived one), after writing the note to the ticket file and without committing it, despite `TASK-355`. So every worktree created before an archive on `main` cannot edit any ticket until it merges `main`.

Escape: introduced by `TASK-356`, whose cross-branch `lookup` in `check` made archiving a referenced ticket fail. Cold read by a Haiku subagent, 2026-11-17. Fixed: neither real-Git test failed before the change as first written (a plain archive and a plain edit both work), so the tests now use the reproduction, found by the planner; `autocommit = true` for the clean-status check; tie-breaking and detached HEAD; how a `Version` maps back to a ticket and which historical versions are candidates; the outcome when another branch edits an archived ticket (accepted, stated). Not adopted: a repository-level property over `tasks`; the unit properties and two real tests cover it.

## History

- 2026-11-17T19:53:05Z kind-umber-toad → todo
- 2026-11-17T19:59:48Z kind-umber-toad: changed priority, notes
- 2026-11-17T20:00:40Z kind-umber-toad: changed title, description, acceptance criteria
- 2026-11-17T20:00:40Z kind-umber-toad todo → planning
- 2026-11-17T20:00:42Z kind-umber-toad: changed owner
- 2026-11-17T20:00:42Z kind-umber-toad planning → cold-read
- 2026-11-17T20:05:01Z kind-umber-toad: changed labels, description, acceptance criteria, notes
- 2026-11-17T20:05:01Z kind-umber-toad cold-read → planning
- 2026-11-17T20:22:20Z kind-umber-toad: changed owner
- 2026-11-17T20:22:20Z kind-umber-toad planning → todo
- 2026-11-17T22:03:54Z witty-ochre-yellowhammer todo → doing
