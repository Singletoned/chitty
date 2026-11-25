---
title: Write one-ticket commands to the current branch's copy on every branch except `main` and `task-<n>`
status: doing
labels:
  - bug
priority: high
parent: TASK-602
created: 2026-11-25
moved_from: TASK-YCGMCS
---

## Description

Rule (the person, 2026-11-23 and 2026-11-25): on a branch, Chitty's changes to a ticket go to that branch, to be merged in. This ticket applies it to every branch except the configured main branch and ticket branches; those follow in TASK-602, with the warnings that need TASK-604.

Today only `chitty edit` on `plan/...` branches does this (TASK-521: `Repo.planning_branch`, `Repo.edit_planning`, `Repo.find_for_show` in `src/chitty/store.py`, chosen inside the CLI `edit` command near `src/chitty/cli.py:845`). `chitty note`, `chitty archive <ID>`, the MCP `edit`, `note`, `archive` and `show` tools, and `chitty edit` on other branches such as `hotfix/...` refuse with `<ID>'s latest committed version is on branch main; run Chitty in worktree <main checkout>`, so planners write from the main checkout, which commits on `main` (seen 2026-11-25 in inbox triage, and in shelfpath as TASK-662).

Change, keeping `cli.py` and `mcp.py` thin:

- `Repo.planning_branch()` (rename it if a clearer name fits) returns the current branch unless it is `None`, the configured main branch, or a ticket branch: a name that is some ticket's ID lowercased, as the runner names them (`str(task_id).lower()`, for example `task-602`). Ticket branches are unchanged: workers there already write their own ticket on that branch.
- `Repo.edit_current(task_id, edit) -> tuple[Change, bool]`: on such a branch, `edit_planning(...)`; otherwise `(edit(...), False)`. The `bool` means a run holds the ticket's lock.
- `Repo.archive_current(task_id) -> Change`: on such a branch, take the working-tree copy (`_working_task`, refusing as `edit_planning` does when there is none), run `_reject_planning_conflicts`, and move it to the archive directory; `_set_archived` takes the `StoredTask` instead of calling `find` and `_require_current_version`. With `archive = "delete"` it refuses on such a branch (`archiving on a branch needs archive = "move"`), leaving `_delete_done` untouched. Otherwise, `archive`.
- CLI `edit` (not `--human`, as today) and `note`, and MCP `edit` and `note`, call `edit_current`; CLI and MCP `archive` with an ID call `archive_current`; MCP `show` calls `find_for_show`. The CLI keeps its lock warning for `edit` and `note`.
- `Repo.edit`, `Repo.archive` and `Repo.find` are unchanged, so the runner (`src/chitty/run.py`) and `--human` edits keep today's behaviour.

No property test: a small fixed set of commands and branch names over real Git, each listed in a criterion.

Out of scope: the main branch, ticket branches and warnings instead of refusals (TASK-602); `chitty archive` with no ID; landing a branch (TASK-340); identical copies refused as "changed on both" (TASK-667).

## Acceptance Criteria

- [ ] A real-Git test in `tests/test_planning_worktrees.py`, run once on a `plan/x` branch and once on a `hotfix/x` branch made from `main`, with a numbered ticket committed on `main`: `chitty note`, `chitty edit` and `chitty archive` on that ticket succeed, commit on that branch, and leave `main` unchanged. The `note`, `archive` and `hotfix/x` cases fail today with `latest committed version is on branch main`.
- [ ] The same `hotfix/x` setup through `chitty.mcp`: the `edit`, `note` and `archive` tools succeed and commit on that branch, and `show` returns the checkout's copy after the edit. Fails today.
- [ ] Regression tests: the existing tests in `tests/test_planning_worktrees.py` pass, including `test_main_conflict`, `test_sibling_rename_conflict` and `test_no_local_copy_refuses_edit_but_show_falls_back`; `make check` passes.

## Plan

Add real-Git CLI and MCP regression tests, confirm failures, then route branch-local edits and archives through shared Repo methods while preserving main and ticket branch behaviour. Run formatting and checks, commit, and hand off for review.

## Notes

Regression tests failed before the fix: CLI note on plan/one and hotfix/x and MCP edit on hotfix/x all refused the main branch version.

## History

- 2026-11-25T22:56:47Z calm-ochre-quail → planning
- 2026-11-25T22:57:01Z calm-ochre-quail: changed acceptance criteria
- 2026-11-25T22:57:01Z calm-ochre-quail planning → cold-read
- 2026-11-25T22:57:50Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-25T22:57:50Z calm-ochre-quail cold-read → planning
- 2026-11-25T22:57:58Z calm-ochre-quail planning → cold-read
- 2026-11-25T22:59:10Z calm-ochre-quail: changed description
- 2026-11-25T22:59:10Z calm-ochre-quail cold-read → todo
- 2026-11-25T22:59:30Z calm-ochre-quail: renumbered from TASK-YCGMCS
- 2026-11-25T23:05:58Z calm-ochre-quail: changed title, parent, description, acceptance criteria
- 2026-11-25T23:05:58Z calm-ochre-quail todo → planning
- 2026-11-25T23:06:04Z calm-ochre-quail planning → cold-read
- 2026-11-25T23:06:36Z calm-ochre-quail: changed title, description
- 2026-11-25T23:06:36Z calm-ochre-quail cold-read → planning
- 2026-11-25T23:06:46Z calm-ochre-quail: changed description
- 2026-11-25T23:07:03Z calm-ochre-quail: changed description
- 2026-11-25T23:07:15Z calm-ochre-quail planning → todo
- 2026-11-25T23:24:56Z eager-russet-quail todo → doing
- 2026-11-25T23:27:33Z eager-russet-quail: wrote the plan
- 2026-11-25T23:28:08Z eager-russet-quail: changed notes
