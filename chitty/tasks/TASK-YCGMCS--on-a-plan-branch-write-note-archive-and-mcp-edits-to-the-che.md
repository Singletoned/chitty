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

On a `plan/...` branch, `chitty edit` writes the checkout's own copy of a ticket (TASK-521: `Repo.planning_branch`, `Repo.edit_planning`, `Repo.find_for_show` in `src/chitty/store.py`). But that choice is made in the CLI's `edit` command (`src/chitty/cli.py` around line 845), so the other one-ticket writes skip it:

- `chitty note` (`cli.py` `note`, calls `repo.edit`);
- `chitty archive <ID>` (`repo.archive` -> `Repo._set_archived`, which uses `find` and `_require_current_version`);
- the MCP `edit`, `note` and `archive` tools, and MCP `show` (`src/chitty/mcp.py`, call `repo.edit`, `repo.archive`, `repo.find`).

Each refuses with `<ID>'s latest committed version is on branch main; run Chitty in worktree <main checkout>`, so a planner has to write from the main checkout, which commits on `main`. Seen 2026-11-25 during inbox triage (notes on TASK-676, TASK-594, TASK-472) and in shelfpath (TASK-662, `chitty archive` on a `plan/` branch).

Change: move the `plan/` choice from `cli.py` into the store, so the CLI and MCP share it (`cli.py` and `mcp.py` stay thin). On a `plan/` branch, without `--human`, `Repo.edit` and `Repo.archive` for one ticket act on the working-tree copy, after `_reject_planning_conflicts`, as `edit_planning` does today; MCP `show` uses `find_for_show`. Keep the CLI warning when a run holds the ticket's lock, for `edit` and `note`. Off `plan/` branches nothing changes.

No property test: the inputs are a small fixed set of commands over real Git processes, each listed in a criterion.

Out of scope: other branches and the warnings instead of refusals (TASK-602, which generalises this rule), `chitty archive` with no ID, landing a plan branch (TASK-340).

## Acceptance Criteria

- [ ] A real-Git test in `tests/test_planning_worktrees.py`: on a `plan/x` branch made from `main`, with a numbered ticket committed on `main`, `chitty note` and `chitty archive` on that ticket succeed, commit on `plan/x`, and leave `main` unchanged. Fails today with `latest committed version is on branch main`.
- [ ] The same setup through `chitty.mcp`: the `edit` and `note` tools succeed and commit on `plan/x`, and `show` returns the checkout's copy after the edit. Fails today.
- [ ] Regression tests: the existing tests in `tests/test_planning_worktrees.py` pass, including the refusal when another branch changed the ticket since the split; `make check` passes.

## History

- 2026-11-25T22:56:47Z calm-ochre-quail → planning
