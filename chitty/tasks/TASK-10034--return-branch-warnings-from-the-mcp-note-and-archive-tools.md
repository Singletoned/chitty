---
title: Return branch warnings from the MCP `note` and `archive` tools
status: todo
depends_on:
  - TASK-602
created: 2026-11-25
moved_from: TASK-N6YMT2
---

## Description

TASK-602 puts branch warnings (and TASK-10040 adds them on ticket branches) (`<ID> also changed on <ref> (status there: <status>); merge or rebase it now and resolve any conflict`, built by `branch_change_warning` in `src/chitty/store.py`) into `Change.warnings`. The MCP `edit` tool in `src/chitty/mcp.py` already adds `"warnings": [...]` to its result when `change.warnings` is not empty. The `note` tool, and the `archive` tool given an `id`, return only `change.task.as_dict()`, so an MCP agent writing a ticket that another branch changed gets no signal.

Change, in `src/chitty/mcp.py`: `note`, and `archive` with an `id`, add `"warnings": list(change.warnings)` to the result when it is not empty, as `edit` does. Put the shared step in one small helper and use it in all three tools, replacing the inline block in `edit`. `archive` with no `id` is unchanged.

Test, in `tests/test_planning_worktrees.py`, reusing `test_main_conflict`'s setup (`main` changes TASK-1 after the plan branch splits): from the plan worktree, `mcp.note("TASK-1", "Draft")` returns a result whose `result["warnings"]` is exactly `[branch_change_warning(TaskId("TASK", 1), "refs/heads/main", "todo")]`. Then `mcp.archive("TASK-1")` on the same `todo` ticket (a branch archive needs no `done`) returns exactly the same list. This fails before the change with `KeyError: 'warnings'` (TASK-602 landed). Regression test: in `test_mcp_one_ticket_commands_on_hotfix` (no conflict), capture the results of `mcp.edit`, `mcp.note` and `mcp.archive` and assert that none has a `warnings` key. No property: a fixed Git state.

## Acceptance Criteria

- [ ] The MCP `note` and `archive` warning checks pass and fail before the change with `KeyError` (record it in a note); the hotfix regression test passes
- [ ] `make check` passes

## History

- 2026-11-25T23:30:44Z calm-ochre-quail → backlog
- 2026-11-25T23:32:09Z calm-ochre-quail: renumbered from TASK-N6YMT2
- 2026-11-26T18:02:47Z brisk-bronze-adder: changed dependencies, description
- 2026-11-26T18:03:07Z brisk-bronze-adder: changed dependencies, notes
- 2026-11-26T18:13:23Z brisk-bronze-adder backlog → planning
- 2026-11-26T18:13:55Z brisk-bronze-adder: replaced notes; changed title, dependencies, description, acceptance criteria
- 2026-11-26T18:13:55Z brisk-bronze-adder planning → cold-read
- 2026-11-26T18:16:25Z brisk-bronze-adder cold-read → planning
- 2026-11-26T18:16:49Z brisk-bronze-adder: changed dependencies, description
- 2026-11-26T18:16:49Z brisk-bronze-adder planning → todo
