---
title: Make `chitty path` use the branch's own copy on a `plan/` branch, as `show` does
status: todo
labels:
  - bug
depends_on:
  - TASK-602
created: 2026-11-25
moved_from: TASK-N8MC9A
---

## Description

On a `plan/` or `hotfix/` branch, `chitty path <ID>` prints the file name from `main` after the ticket was retitled on the branch, so `chitty check "$(chitty path <ID>)"` fails with `not a task file in any chitty context` (seen 2026-11-24 for TASK-658 and 2026-11-25 for TASK-10027). `chitty show` in the same worktree gives the right path.

Cause: `path` in `src/chitty/cli.py` and the MCP `path` tool in `src/chitty/mcp.py` call `repo.find(...)`, while `show` calls `repo.find_for_show(...)`, which uses the branch's own copy (TASK-10027). Change both `path` commands to call `find_for_show`. Under the rule in `docs/plan/principles.md`, work off `main` reads its own branch's copy.

Test, in `tests/test_planning_worktrees.py`, extending `test_isolated_edit_and_show`: after the retitle, from the plan worktree, `chitty path TASK-1` prints `self.plan / "chitty/tasks/TASK-1--draft-title.md"`, and so does the MCP `path` tool, called as the MCP tests in that file call other tools. Both fail before the change: they print `<plan worktree>/chitty/tasks/TASK-1--first.md` (the worktree root, but `main`'s file name). No property: one fixed Git state.

Out of scope: ticket branches (TASK-10040 changes `find_for_show` there, and `path` follows it) and TASK-494.

## Acceptance Criteria

- [ ] The CLI and MCP `path` checks in `test_isolated_edit_and_show` pass, and fail before the change (record it in a note)
- [ ] `make check` passes

## History

- 2026-11-25T22:28:41Z calm-ochre-quail → backlog
- 2026-11-25T22:28:43Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:20Z calm-ochre-quail: changed labels, dependencies, notes
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-N8MC9A
- 2026-11-25T23:06:31Z calm-ochre-quail: changed notes
- 2026-11-26T18:02:38Z brisk-bronze-adder: changed notes
- 2026-11-26T18:08:00Z brisk-bronze-adder backlog → planning
- 2026-11-26T18:08:04Z brisk-bronze-adder: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T18:08:04Z brisk-bronze-adder planning → cold-read
- 2026-11-26T18:09:17Z brisk-bronze-adder cold-read → planning
- 2026-11-26T18:09:20Z brisk-bronze-adder: changed description
- 2026-11-26T18:09:20Z brisk-bronze-adder planning → todo
