---
title: Write one-ticket commands to the current branch's copy on every branch except `main`
status: planning
labels:
  - bug
priority: high
parent: TASK-602
created: 2026-11-25
moved_from: TASK-YCGMCS
---

## Description

Rule (the person, 2026-11-23 and 2026-11-25): on a branch, Chitty's changes to a ticket go to that branch, to be merged in. This ticket applies it to every branch except the configured main branch; `main` follows in TASK-602, with the warnings that need TASK-604.

Today only `plan/...` branches get it, and only for `chitty edit` (TASK-521: `Repo.planning_branch`, `Repo.edit_planning`, `Repo.find_for_show` in `src/chitty/store.py`, chosen inside the CLI `edit` command around `src/chitty/cli.py` line 845). Everything else refuses with `<ID>'s latest committed version is on branch main; run Chitty in worktree <main checkout>`, so a planner has to write from the main checkout, which commits on `main`:

- `chitty note` (calls `repo.edit`), `chitty archive <ID>` (`repo.archive` -> `Repo._set_archived`);
- the MCP `edit`, `note`, `archive` and `show` tools (`src/chitty/mcp.py`);
- `chitty edit` on any branch not named `plan/...`, such as `hotfix/...`.

Seen 2026-11-25 during inbox triage (notes on TASK-676, TASK-594, TASK-472) and in shelfpath (TASK-662).

Change, keeping `cli.py` and `mcp.py` thin:

- `Repo.planning_branch()` (rename it if a clearer name fits, for example `local_write_branch`) returns the current branch when it is neither the configured main branch nor `None`, instead of only `plan/...` branches. On the ticket's own `task-<n>` branch, keep today's path for that ticket (`Repo.edit`/`find`, which already write that branch), so a worker is not refused when `main` changed its ticket; a runner claim on `main` must not block the worker.
- Add `Repo.edit_current(task_id, edit) -> tuple[Change, bool]`: on such a branch it returns `edit_planning(...)`; otherwise `(edit(...), False)`. The `bool` is "a run holds the ticket's lock", as `edit_planning` returns today.
- Add `Repo.archive_current(task_id) -> Change`: on such a branch it takes the working-tree copy (`_working_task`), refusing as `edit_planning` does when there is none, runs `_reject_planning_conflicts`, and moves that copy to the archive directory; `_set_archived` takes the `StoredTask` instead of calling `find` and `_require_current_version` for it. With `archive = "delete"` it refuses on such a branch (`archiving on a branch needs archive = "move"`), so `_delete_done` and its dependency cleanup are untouched. Otherwise it calls `archive`.
- CLI `edit` (when not `--human`, as today) and `note`, and MCP `edit` and `note`, call `edit_current`. CLI `archive <ID>` and MCP `archive` with an ID call `archive_current`. MCP `show` calls `find_for_show`. The CLI prints its existing lock warning for `edit` and `note`; MCP and `archive` do not warn.
- `Repo.edit`, `Repo.archive` and `Repo.find` are unchanged, so the runner (`src/chitty/run.py`) and `--human` edits keep today's cross-branch behaviour.

No property test: the inputs are a small fixed set of commands and branch names over real Git processes, each listed in a criterion.

Out of scope: the configured main branch, and warnings instead of refusals (both TASK-602); `chitty archive` with no ID; landing a branch (TASK-340); identical copies refused as "changed on both" (TASK-667).

## Acceptance Criteria

- [ ] A real-Git test in `tests/test_planning_worktrees.py`, run once on a `plan/x` branch and once on a `hotfix/x` branch made from `main`, with a numbered ticket committed on `main`: `chitty note`, `chitty edit` and `chitty archive` on that ticket succeed, commit on that branch, and leave `main` unchanged. The `note`, `archive` and `hotfix/x` cases fail today with `latest committed version is on branch main`.
- [ ] The same `hotfix/x` setup through `chitty.mcp`: the `edit`, `note` and `archive` tools succeed and commit on that branch, and `show` returns the checkout's copy after the edit. Fails today.
- [ ] Regression tests: the existing tests in `tests/test_planning_worktrees.py` pass, including `test_main_conflict`, `test_sibling_rename_conflict` and `test_no_local_copy_refuses_edit_but_show_falls_back`; `make check` passes.

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
