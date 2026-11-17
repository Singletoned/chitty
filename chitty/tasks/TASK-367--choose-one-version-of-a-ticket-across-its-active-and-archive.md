---
title: Choose one version of a ticket across its active and archive directories
status: cold-read
labels:
  - bug
priority: high
owner: planner-cold-read
created: 2026-11-17
---

## Description

Seen twice on 2026-11-17. On `main`, `chitty archive TASK-326` (and `TASK-356`) moved the file to `chitty/tasks/archive/`, then failed with `TASK-326 is used by more than one file: chitty/tasks/TASK-326--....md, chitty/tasks/archive/TASK-326--....md` and committed nothing, leaving `main` dirty. That dirty state, for `TASK-342`, is what made `chitty run` fail to land `TASK-326`. In the `task-364` worktree, which was made before `TASK-356` was archived on `main`, every `chitty edit` failed with `TASK-356 is used by more than one file`, naming the worktree's active file and `main`'s archived one.

Cause: `_tasks_in_location` in `src/chitty/store.py` picks one version per ticket for the active directory and, separately, for the archive directory, each from the current checkout's files and every branch's committed versions (`git.historical_files`). `lookup` then refuses any ticket found in both. After an archive, other branches still have the active file, and branches made earlier still have it locally.

Decisions:

- Choose one version per ticket across both directories of a context, with the rule `_tasks_in_location` already uses, as a pure function in `src/chitty/store.py`:
  - `Version`: a frozen dataclass of `path: Path`, `archived: bool`, `local: bool` (a file in the current checkout), `dirty: bool` (local and changed or untracked in Git), `branch: str | None` (for a historical version, the ref it came from), `committed_at: int | None` (for a historical version).
  - `choose_version(versions: Sequence[Version], current_branch: str | None) -> Version`. More than one local version raises `ChittyError` with the existing `<ID> is used by more than one file: <paths>` text: that is a real duplicate in this checkout. Otherwise a dirty local version wins. Otherwise, when the newest historical version (greatest `committed_at`) is on a branch other than `current_branch`, it wins. Otherwise the local version wins, or the newest historical version when there is no local one.
- `tasks`, `all_tasks` and `lookup` use it, so a ticket appears once, as active or archived by the chosen version. The `which` filter in `tasks` applies after choosing. Keep the per-location cache, or cache per context.
- No change to `git.historical_files`, or to how a ticket the current branch has changed beats `main` (`TASK-356`).

Tests: Hypothesis properties for `choose_version` in a new `tests/test_property_choose_version.py`, over lists of versions with at most one local version, random branches from a small set and random times: the result is one of the inputs; a dirty local version always wins; shuffling the input does not change the result; adding a historical version older than every other version does not change the result. An example test that two local versions raise. Real-Git tests in a new `tests/test_archive_across_branches.py`, in the style of `tests/test_check_cross_branch_references.py`: with another branch still holding the active file, `chitty archive` on `main` succeeds, commits, and leaves `git status` clean; in a worktree made before that archive, `chitty edit` of a different ticket succeeds and `chitty show` of the archived one reports it archived. Both fail before the change. Add `Version` and `choose_version` first, raising `NotImplementedError`, so the property tests fail on behaviour rather than import.

Out of scope: a failed write leaving its file uncommitted (a separate ticket), and picking versions by ref tip instead of newest commit (`TASK-366`).

## Acceptance Criteria

- [ ] Hypothesis properties in `tests/test_property_choose_version.py` show `choose_version` returns an input, lets a dirty local version win, ignores order and ignores an older historical version; two local versions raise; the tests fail with the stub
- [ ] In `tests/test_archive_across_branches.py`, `chitty archive` on `main` succeeds and leaves `git status` clean while another branch holds the active file, and an older worktree can `chitty edit` another ticket and `chitty show` the archived one as archived; the tests fail before the change
- [ ] `make check` passes

## Notes

Also seen 2026-11-17: in the `task-364` worktree, which branched before `TASK-356` was archived on `main`, `chitty edit TASK-364 --note ...` failed with `TASK-356 is used by more than one file` (the local active file and `main`'s archived one), after writing the note to the ticket file and without committing it, despite `TASK-355`. So every worktree created before an archive on `main` cannot edit any ticket until it merges `main`.

## History

- 2026-11-17T19:53:05Z kind-umber-toad → todo
- 2026-11-17T19:59:48Z kind-umber-toad: changed priority, notes
- 2026-11-17T20:00:40Z kind-umber-toad: changed title, description, acceptance criteria
- 2026-11-17T20:00:40Z kind-umber-toad todo → planning
- 2026-11-17T20:00:42Z kind-umber-toad: changed owner
- 2026-11-17T20:00:42Z kind-umber-toad planning → cold-read
