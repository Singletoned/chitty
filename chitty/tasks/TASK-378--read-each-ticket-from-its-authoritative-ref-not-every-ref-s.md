---
title: Read each ticket from its authoritative ref, not every ref's history
status: planning
depends_on:
  - TASK-377
  - TASK-382
  - TASK-383
parent: TASK-376
created: 2026-11-18
---

## Description

Today `Repo._tasks_in_location` and `Repo.discovered_contexts` in `src/chitty/store.py` read every local and remote-tracking ref's history (`self._history()`, from `git.historical_files`) and take each ticket's copy with the newest commit time, overlaid with this checkout's files. Commit time is not causal order, so this picks wrong copies (`TASK-366`). The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) reads each ticket from one authoritative place, chosen by `ticket_source` (`TASK-377`).

Starts after `TASK-377`, `TASK-382` and `TASK-383` land. The last two stop the runner writing on `main` for tickets with a branch; without them, an error the runner records on `main` would be hidden behind the branch copy.

Decisions:

- Branches: enumerate with full ref names (`refs/heads/...`, `refs/remotes/...`, skipping symbolic refs such as `origin/HEAD`) and strip the prefix; never use `%(refname:short)`, which can print `heads/origin/task-5`. A ticket branch is a local branch, or a remote-tracking branch after its first `/`, whose name is a configured context prefix plus `-<suffix>`, lower-cased (`task-5`, `origin/task-5`; not `task-5-fix` or `plan/ticket-state`).
- Which ticket IDs exist: every ticket file in this checkout's working tree, in `main`'s tip tree, and, for each ticket branch, that branch's own ticket at its tip. Contexts are discovered from the same three places. A ticket only on some other branch is not listed.
- Once per `Repo` (cached like today, cleared by `_invalidate`), build a map from ID to source and file: call `ticket_source` for each ID with whether its copy (this checkout's, else main's or its branch's) has `provisional: true` (`TASK-380`; pass `False` until it lands), `git.current_branch`, `Repo._main_branch()`, the branch tips, and `contains` backed by `git merge-base --is-ancestor`, called only for an ID with several candidates. Add the Git helpers to `src/chitty/git.py`. Build each location's list (`_tasks_in_location`) from that map, so an ID is listed once, in whichever directory (active or archive, any context) holds its source copy. The same ID in both directories of its source stays the existing `used by more than one file` error.
- `WORKING_TREE`: read this checkout's file, committed or not. A ref: read the file at that ref's tip (`git ls-tree` on the ticket directories, then `git cat-file --batch`). If the source has no file for the ID (deleted there), the ticket is not listed.
- So on a branch that is neither `main` nor the ticket's own branch, an existing ticket is read from `main`'s tip, and an uncommitted edit to it in this checkout is not shown. Intended: the rule makes that copy not the ticket.
- `StoredTask.branch` is the source ref, or `None` for `WORKING_TREE`; `show` prints `branch: <ref>` for it, and `_require_current_version` keeps guarding writes until `TASK-385` replaces it. `StoredTask.path` is this checkout's root joined with the source copy's relative path, whether or not that file exists here.
- `ticket_source`'s `ChittyError` for diverged branches propagates from every read that reaches that ticket (`show`, `list`, `next`, `run`), loudly, as errors should be.
- Outside a Git repository every ticket is read from the working tree, as today.
- Unchanged here: `next_number` keeps its `_history()` loop until `TASK-379`; `check.py`'s `check` and `fix` scan this checkout's files as today (`TASK-394` limits `fix`); `_dependency_is_done` keeps reading dependencies from `main`'s files, because done means landed on `main`; `TASK-386` deletes the history code.
- Migrate the existing tests that assert the old choice or visibility, including in `tests/test_check_cross_branch_references.py` the "other branch" row of `test_reference_existence_matches_show`, `test_malformed_task_on_another_branch_reports_parse_error` and `test_edit_can_depend_on_task_only_on_main`, and any in `tests/test_store.py` and `tests/test_cli.py`. Keep `tests/test_list_performance.py` passing.

Tests: real-Git tests in a new `tests/test_ticket_reads.py`, inheriting `RepoTestCase` from `tests/support.py`, one test per placement in the criteria, with `GIT_COMMITTER_DATE` set on commits where order matters. Commit `main`'s copy directly with Git where `chitty edit` on `main` would be refused. A generated property over placements is `TASK-393`. No property here: a fixed set of placements, each listed and tested.

## Acceptance Criteria

- [ ] From the main checkout: a ticket only on `main` reads `main`'s copy; a ticket edited on `task-<n>`, with `main`'s copy committed later by `GIT_COMMITTER_DATE`, reads the branch copy and `chitty show` prints `branch: task-<n>` (fails before the change); a ticket only on `origin/task-<n>` ahead of `main` reads that copy; local `task-<n>` behind `origin/task-<n>` reads the remote copy; a ticket only on an unrelated branch is not listed by `chitty list`
- [ ] A ticket archived on its branch but active on `main` is listed once, as archived, by `chitty list --all` in the main checkout; a `todo` ticket whose branch says `doing` lists as `doing`; a ticket whose branch deletes its file is not listed
- [ ] In the linked worktree of `task-5`, `TASK-5` shows an uncommitted edit made there, and `TASK-7` (no branch) shows `main`'s tip copy even though the worktree's copy differs; on a branch `feature`, an existing ticket shows `main`'s copy
- [ ] With local `task-<n>` and `origin/task-<n>` diverged, `chitty show` and `chitty list` in the main checkout fail naming both; outside a Git repository tickets read from the working tree; with `git.historical_files` patched to raise, `chitty show` and `chitty list` still work; `make check` passes

## History

- 2026-11-18T16:20:04Z lively-quartz-crane → backlog
- 2026-11-18T16:20:27Z lively-quartz-crane: changed title
- 2026-11-18T16:23:16Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:32:51Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:32:51Z lively-quartz-crane backlog → planning
- 2026-11-18T16:33:20Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:38:58Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:38:58Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:39:00Z lively-quartz-crane: changed acceptance criteria
