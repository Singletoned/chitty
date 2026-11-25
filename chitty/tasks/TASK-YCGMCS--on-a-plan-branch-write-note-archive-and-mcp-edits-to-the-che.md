---
title: On a `plan/` branch, write `note`, `archive` and MCP edits to the checkout's copy, as `edit` does
status: planning
labels:
  - bug
priority: high
created: 2026-11-25
provisional: true
---

## Description

On a `plan/...` branch, `chitty edit` writes the checkout's own copy of a ticket (TASK-521: `Repo.planning_branch`, `Repo.edit_planning`, `Repo.find_for_show` in `src/chitty/store.py`). That choice is made inside the CLI `edit` command (`src/chitty/cli.py` around line 845), so the other one-ticket front-end commands skip it and refuse with `<ID>'s latest committed version is on branch main; run Chitty in worktree <main checkout>`:

- `chitty note` (`cli.py` `note`, calls `repo.edit`);
- `chitty archive <ID>` (`repo.archive` -> `Repo._set_archived`);
- the MCP `edit`, `note`, `archive` and `show` tools (`src/chitty/mcp.py`).

So a planner has to write from the main checkout, which commits on `main`. Seen 2026-11-25 during inbox triage (notes on TASK-676, TASK-594, TASK-472), and in shelfpath (TASK-662, `chitty archive` on a `plan/` branch).

Change, keeping `cli.py` and `mcp.py` thin:

- Add `Repo.edit_current(task_id, edit) -> tuple[Change, bool]`: on a `plan/` branch it returns `edit_planning(...)`; elsewhere `(edit(...), False)`. The `bool` is "a run holds the ticket's lock", as `edit_planning` returns today.
- Add `Repo.archive_current(task_id) -> Change`: on a `plan/` branch it archives the working-tree copy after `_reject_planning_conflicts`, refusing as `edit_planning` does when there is no local copy; elsewhere it calls `archive`.
- CLI `edit` (when not `--human`, as today) and `note`, and MCP `edit` and `note`, call `edit_current`. CLI `archive <ID>` and MCP `archive` with an ID call `archive_current`. MCP `show` calls `find_for_show`. The CLI prints its existing lock warning for `edit` and `note`; MCP and `archive` do not warn.
- `Repo.edit`, `Repo.archive` and `Repo.find` are unchanged, so the runner (`src/chitty/run.py`) and `--human` edits keep today's cross-branch behaviour.

No property test: the inputs are a small fixed set of commands over real Git processes, each listed in a criterion.

Out of scope: branches other than `plan/`, and warnings instead of refusals (TASK-602 generalises this rule); `chitty archive` with no ID; landing a plan branch (TASK-340).

## Acceptance Criteria

- [ ] A real-Git test in `tests/test_planning_worktrees.py`: on a `plan/x` branch made from `main`, with a numbered ticket committed on `main`, `chitty note` and `chitty archive` on that ticket succeed, commit on `plan/x`, and leave `main` unchanged. Fails today with `latest committed version is on branch main`.
- [ ] The same setup through `chitty.mcp`: the `edit`, `note` and `archive` tools succeed and commit on `plan/x`, and `show` returns the checkout's copy after the edit. Fails today.
- [ ] Regression tests: the existing tests in `tests/test_planning_worktrees.py` pass, including `test_main_conflict`, `test_sibling_rename_conflict` and `test_no_local_copy_refuses_edit_but_show_falls_back`; `make check` passes.

## History

- 2026-11-25T22:56:47Z calm-ochre-quail → planning
- 2026-11-25T22:57:01Z calm-ochre-quail: changed acceptance criteria
- 2026-11-25T22:57:01Z calm-ochre-quail planning → cold-read
- 2026-11-25T22:57:50Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-25T22:57:50Z calm-ochre-quail cold-read → planning
