---
title: Sync a ticket file newer on `main` into its worktree before a work session
status: planning
labels:
  - bug
priority: high
created: 2026-11-18
---

## Description

Seen 2026-11-17 on `TASK-343`. An error repair committed `error → todo` to the ticket on `main` after the branch `task-343` last committed it. The next `chitty run` ran `check` in the worktree, then the claim (`work_repo.edit(action.id, claim_edit())` in `_run_ticket`, `src/chitty/run.py`) failed with `TASK-343's latest committed version is on branch main; run Chitty in worktree <main checkout>` (`Repo._require_current_version`, `src/chitty/store.py`) and stopped `chitty run --loop`. An `error` ticket hits no error, because the repair handoff uses `skip_current_version`, but its repair agent starts on the stale copy.

Principle (decided 2026-11-18): bringing a ticket branch up to date is mechanical and done by the runner; only code conflicts go to an agent. The ticket file is Chitty's own data, so the runner can always bring it up to date from `main`.

Decisions:

- Sync only from `main_branch`. Versions newest on other branches or remote-tracking refs are not synced; the run behaves as today.
- Pure function `should_sync(found_branch: str | None, main_branch: str, ticket_dirty: bool) -> bool` in `src/chitty/run.py`: true exactly when `found_branch == main_branch` and not `ticket_dirty`. `found_branch` is `Repo.open(worktree).find(task_id).branch`, which is `None` when the worktree's own copy is current.
- `ticket_dirty` is true when `git status --porcelain -- <ticket directory>` lists any path for that ticket ID (modified, staged, untracked or deleted). Run it through `_git`, which raises on failure; do not use `git.dirty_paths`, which returns an empty set on error.
- `_sync_ticket(worktree: Path, task_id: TaskId, main_branch: str) -> None` in `src/chitty/run.py`. When `should_sync` holds, it checks out `main_branch`'s file for that ID with `git checkout <main_branch> -- <path>` (so the bytes are exact), runs `git rm` on the worktree's file for that ID when its path differs (a title change, archive or move on `main`), and commits only those paths with the message `chitty: sync <ID> from <main_branch>` and a `Task: <ID>` trailer. Any Git failure raises `ChittyError` naming the path.
- Call it in work mode only, in `_run_ticket`, after `setup` and before `work_repo = Repo.open(worktree)`, so the repo it opens sees the synced file. Every ticket status. `TASK-370` will also call it after an aborted merge.
- When `ticket_dirty`, the run continues as today: the claim may edit a dirty file, and a deleted file still fails the claim with the stale-copy error.

Out of scope: merging `main` in work mode (`TASK-370`), review mode (`TASK-359`), detached `HEAD`, and non-UTF-8 ticket files.

Tests:

- Hypothesis property for `should_sync` in a new `tests/test_property_should_sync.py`: generate `found_branch` from `None`, `main_branch` and other names, and `ticket_dirty`; the result is true exactly when `found_branch == main_branch` and not dirty. Add `should_sync` first, raising `NotImplementedError`.
- Real-Git, fake-agent runner tests in a new `tests/test_run_syncs_ticket.py`, in the style of `tests/test_review_merge.py`. The fake agent copies the worktree ticket file to a marker file when it starts, so tests can see what it saw. Commit `main`'s edit with a later `GIT_COMMITTER_DATE` than the branch's, as `tests/test_store.py` does; commits in the same second tie.

## Acceptance Criteria

- [ ] The `should_sync` property in `tests/test_property_should_sync.py` passes and fails against the `NotImplementedError` stub, and `make check` passes
- [ ] The `TASK-343` case: a `todo` ticket whose branch exists, with a later edit to the ticket on `main`; a work run commits `chitty: sync TASK-<n> from main` touching only the ticket file, the agent marker equals `git show main:<path>` byte for byte apart from the claim, and the ticket is `doing`; a second run adds no sync commit; the test fails before the change
- [ ] The same state on an `error` ticket: the repair agent marker equals `git show main:<path>` byte for byte; the test fails before the change on that assertion
- [ ] After a title change to the ticket on `main`, a work run leaves exactly one file for that ticket ID in the worktree, at `main`'s path
- [ ] With the worktree ticket file modified but uncommitted, no sync commit is made and the file is not replaced by `main`'s copy

## Notes

Superseded 2026-11-18 by the rebase design: `TASK-372` claims on `main` first, and `TASK-370` rebases the branch onto `main`, merging ticket files with `TASK-359`. Copying `main`'s ticket over the branch's would also lose the branch's notes.

## History

- 2026-11-18T09:24:53Z witty-ginger-falcon → cold-read
- 2026-11-18T09:25:14Z witty-ginger-falcon: changed dependencies
- 2026-11-18T09:28:13Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:28:15Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:28:19Z witty-ginger-falcon planning → todo
- 2026-11-18T09:28:25Z witty-ginger-falcon: changed title
- 2026-11-18T09:32:32Z witty-ginger-falcon todo → planning
- 2026-11-18T09:52:27Z witty-ginger-falcon: changed notes
