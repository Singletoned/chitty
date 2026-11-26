---
title: Accept `difficulty` in the MCP add and edit tools, and draw it in ticket strategies
status: cold-read
depends_on:
  - TASK-311
parent: TASK-308
created: 2026-11-26
provisional: true
---

## Description

Part of `TASK-308`, split from `TASK-311`, which adds the `difficulty` field (`DIFFICULTIES = ("low", "medium", "high")` in `src/chitty/model.py`, `Edit.difficulty` in `src/chitty/store.py`, `--difficulty` on the CLI). This ticket gives the MCP tools the same option and lets the ticket strategy draw the field, so the existing parse and render properties cover it.

Change:

- `src/chitty/mcp.py`: `Difficulty = Literal["low", "medium", "high"]`. The add tool takes `difficulty: Difficulty | None = None` and the edit tool `difficulty: Difficulty | Literal[""] | None = None`, passed through as `priority` is. Add `difficulty` to the edit tool's `'' unsets priority/owner/plan` description.
- `tests/ticket_strategies.py`: `_ticket_texts` sometimes adds `difficulty: <one of DIFFICULTIES>`, drawn independently of `priority`, placed straight after the `priority` line (or where it would be), following `FIELD_ORDER`.

Tests: the MCP cases in `tests/test_mcp.py`'s style; a `check_find` case in `tests/test_ticket_strategies.py` beside `test_plan_present`. Without the change, the MCP tools reject or drop the unknown argument and the strategy never draws the line. No new property: the strategy change feeds the existing ones.

Out of scope: the field, CLI and docs (`TASK-311`).

## Acceptance Criteria

- [ ] In `tests/test_mcp.py`: the add tool with `difficulty="medium"` writes it, the edit tool with `difficulty=""` removes it, and the edit tool with `difficulty="hard"` raises `ToolError` matching `difficulty` with the file byte-identical; each fails before the change
- [ ] The new `tests/test_ticket_strategies.py` case finds a drawn text containing `"\ndifficulty: "`, and fails before the change; `make check` passes

## History

- 2026-11-26T20:08:38Z zesty-ginger-newt → planning
- 2026-11-26T20:08:50Z zesty-ginger-newt planning → cold-read
