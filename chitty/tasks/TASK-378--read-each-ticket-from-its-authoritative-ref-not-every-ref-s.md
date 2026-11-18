---
title: Read each ticket from its authoritative ref, not every ref's history
status: todo
labels:
  - needs-minor
depends_on:
  - TASK-377
  - TASK-382
  - TASK-383
  - TASK-396
parent: TASK-376
created: 2026-11-18
---

## Description

Today `Repo._tasks_in_location` and `Repo.discovered_contexts` in `src/chitty/store.py` read every local and remote-tracking ref's history (`self._history()`, from `git.historical_files`) and take each ticket's copy with the newest commit time, overlaid with this checkout's files. Commit time is not causal order, so this picks wrong copies (`TASK-366`). The decided rule (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) reads each ticket from one authoritative place, chosen by `ticket_source` (`TASK-377`), using the Git helpers of `TASK-396`.

Starts after `TASK-377`, `TASK-396`, `TASK-382` and `TASK-383` land. The last two stop the runner writing on `main` for tickets with a branch; without them, an error the runner records on `main` would be hidden behind the branch copy.

Decisions:

- `TASK-396`'s helpers take and return full ref names (`refs/heads/task-5`, `refs/remotes/origin/task-5`); strip the prefixes into `ticket_source`'s `local_tips` and `remote_tips`, and map its short result back to the full name before reading.
- Ticket branches: from `git.branch_tips`, a local branch, or a remote-tracking branch after its first `/`, whose name is a configured context prefix plus `-<suffix>`, lower-cased (`task-5`, `origin/task-5`; not `task-5-fix` or `plan/ticket-state`).
- Which ticket IDs exist: every ticket file in this checkout's working tree, in `main`'s tip tree, and, for each ticket branch, that branch's own ticket at its tip (`git.files_at`): the file whose ID, lower-cased, equals the branch name (`human-12` holds `HUMAN-12`). Ticket files are recognised as `scan` and `ids.parse_filename` do; a file that fails to parse in the copy that is read raises `ChittyError` as `<ref>:<path>: <error>`, as today. Contexts are discovered from the same places. A ticket only on some other branch is not listed.
- Once per `Repo` (cached, cleared by `_invalidate`), build a map from each ID to its source and the list of its files in that source (active and archive directories of any context). Call `ticket_source` for each ID with: `provisional` (pass `False` until `TASK-380` lands; afterwards, the `provisional` field of the copy in this checkout, else of `main`'s copy, else of the branch's); `git.current_branch`; `Repo._main_branch()`; `main_tip` from `git.ref_commit`; the branch tips; `contains(a, b)` as `git.is_ancestor(root, b, a)` (`b` in `a`'s history), called for every ID that has a candidate (rule 2 needs it even for one), and returning `False` when `a` is `None`; and `changed_on_both(ref)`, true when both `git.changed_since_split(root, ref, main, paths)` and `git.changed_since_split(root, main, ref, paths)` are true, where `paths` is the union of this ID's file paths at `main`'s tip and at `ref`'s tip (so an archive on one side and an edit on the other counts). With no `main` commit, `changed_on_both` returns `False` without calling Git, and the read raises `ChittyError` naming `main_branch` only where `TASK-377` says. An ID listed with more than one file in its source stays the existing `used by more than one file` error. `_tasks_in_location` and `lookup` read from the map, so an ID is listed once, in whichever directory holds its source copy; `context_of` takes the context of that copy, falling back to the prefix only when there is none.
- `WORKING_TREE`: read this checkout's file, committed or not; a file deleted there but not committed is not listed. A ref: read the file at that ref's tip. If the source has no file for the ID (deleted there), the ticket is not listed.
- `StoredTask.branch` is the source ref, or `None` for `WORKING_TREE`; `show` prints `branch: <ref>`. `StoredTask.path` is this checkout's root joined with the source copy's relative path, whether or not that file exists here.
- Visible behaviour changes (label `needs-minor`): on a branch that is neither `main` nor the ticket's own branch, an existing ticket is read from `main`'s tip (an uncommitted edit to it there is not shown), and `_require_current_version` then refuses to write it until `TASK-385` replaces the message; a ticket branch merged into `main` no longer hides `main`'s copy; a repository whose configured main branch has no commit (for example one on `master` with the default `main_branch`) now fails reads off `main` with `TASK-377`'s error. `ticket_source`'s errors (diverged branches, a ticket changed on both sides) propagate from every read that reaches that ticket.
- Outside a Git repository every ticket is read from the working tree, as today.
- Unchanged here: `next_number` keeps its `_history()` loop until `TASK-379`; `check.py`'s `check` and `fix` scan this checkout's files (`TASK-394` limits `fix`); `_dependency_is_done` keeps reading dependencies from `main`'s files, because done means landed on `main`; `TASK-386` deletes the history code. Cost: one `is_ancestor` call per ticket that has a ticket branch, and one diff per ticket read from a branch; accepted for now.
- Migrate every existing test that asserts the old choice or visibility to the new behaviour, without deleting or weakening any: in `tests/test_check_cross_branch_references.py`, the "other branch" row of `test_reference_existence_matches_show` (`missing` becomes `True`), `test_malformed_task_on_another_branch_reports_parse_error` (now `no task`), and `test_edit_can_depend_on_task_only_on_main` (now refused on a non-ticket branch); `tests/test_unconfigured_directories.py` `test_finds_directory_that_exists_only_in_branch_history` (now not found); in `tests/test_next.py`, the tests around lines 176-224 on branches `worker`, `rename` and `archive`, including `test_unmerged_archive_does_not_complete_dependency` (writes now refused; reads from `main`); in `tests/test_cli.py` around lines 1790-1863, `test_refuses_all_single_ticket_writes_from_another_worktree`, `test_refuses_a_remote_tracking_branch`, `test_allows_writes_in_the_branch_with_the_latest_version` and `test_allows_writes_from_a_new_worktree_with_no_commits_of_its_own` (their `worker` branches are not ticket branches: rename them to ticket branches where the test is about in-flight tickets, or assert the new refusal); and any others `make check` shows. Keep `tests/test_list_performance.py` passing.
- One ticket, not split: the migrations cannot land apart from the read change without `make check` failing in between.

Tests: real-Git tests in a new `tests/test_ticket_reads.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`, one test per placement in the criteria, `GIT_COMMITTER_DATE` set on commits where order matters, and `main`'s copy committed directly with Git where `chitty edit` on `main` would be refused. The generated property over placements is `TASK-393`. No property here: a fixed set of placements, each listed and tested.

## Acceptance Criteria

- [ ] From the main checkout, with an uncommitted edit to each ticket's file there: a ticket only on `main` shows the uncommitted edit; a ticket edited on `task-<n>` (ahead of `main`) shows the branch copy and `chitty show` prints `branch: task-<n>`, even when a later `main` commit by `GIT_COMMITTER_DATE` touches another ticket; a ticket only on `origin/task-<n>` ahead of `main` shows that copy; local `task-<n>` behind `origin/task-<n>` shows the remote copy (fails before the change); a ticket only on an unrelated branch is not listed (fails before the change)
- [ ] A ticket archived on its branch but active on `main` is listed once, as archived, by `chitty list --all` in the main checkout; a `todo` ticket whose branch says `doing` lists as `doing`; a ticket whose branch deletes its file is not listed; a ticket branch fast-forward merged into `main` and then left behind by a later `main` commit shows `main`'s copy
- [ ] In the linked worktree of `task-5`, after a commit there changing `TASK-5`, `TASK-5` shows a further uncommitted edit made there, and `TASK-7` (no branch) shows `main`'s tip copy despite an uncommitted edit to it in that worktree; on branch `feature`, an existing ticket shows `main`'s tip copy despite an uncommitted edit there
- [ ] With local `task-<n>` and `origin/task-<n>` diverged, or with the ticket edited on both `task-<n>` and `main` since they split, `chitty show` and `chitty list` in the main checkout fail naming the refs; outside a Git repository tickets read from the working tree
- [ ] With `git.historical_files` patched to raise, `chitty show` and `chitty list` still work; every migrated test asserts its new behaviour; `make check` passes

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
- 2026-11-18T16:40:28Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:52:27Z lively-quartz-crane: changed labels, dependencies, description, acceptance criteria
- 2026-11-18T17:52:27Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:52:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:55:29Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:55:29Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:55:31Z lively-quartz-crane planning → todo
