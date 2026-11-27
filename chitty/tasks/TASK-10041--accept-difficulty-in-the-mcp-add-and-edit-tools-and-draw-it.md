---
title: Accept `difficulty` in the MCP add and edit tools, and draw it in ticket strategies
status: doing
depends_on:
  - TASK-311
parent: TASK-308
created: 2026-11-26
moved_from: TASK-KEGB2N
---

## Description

Part of `TASK-308`, split from `TASK-311`, which adds the `difficulty` field (`DIFFICULTIES = ("low", "medium", "high")` in `src/chitty/model.py`, `Edit.difficulty` in `src/chitty/store.py`, `--difficulty` on the CLI). This ticket gives the MCP tools the same option and lets the ticket strategy draw the field, so the existing parse and render properties cover it.

Change:

- `src/chitty/mcp.py`: `Difficulty = Literal["low", "medium", "high"]`. The add tool takes `difficulty: Difficulty | None = None` and the edit tool `difficulty: Difficulty | Literal[""] | None = None`, passed into the add tool's `fields` dict and the edit tool's `Edit` as `priority` is (`Priority` is a plain `str`; the `Literal` here is deliberately stricter). Use `Literal` values matching `DIFFICULTIES`. Add `difficulty` to the edit tool's `'' unsets priority/owner/plan` description.
- `tests/ticket_strategies.py`: `_ticket_texts` sometimes adds `difficulty: <one of DIFFICULTIES>`, drawn independently of `priority`, appended straight after the `priority` draw.

Tests: the MCP cases in `tests/test_mcp.py`'s style; a `check_find` case in `tests/test_ticket_strategies.py` beside `test_plan_present`. Without the change, the add tool silently drops the unknown argument and the edit tool fails with `nothing to change`, and the strategy never draws the line. No new property: the strategy change feeds the existing ones.

Out of scope: the field, CLI and docs (`TASK-311`).

## Acceptance Criteria

- [ ] In `tests/test_mcp.py`: the add tool with `difficulty="medium"` writes it, the edit tool with `difficulty=""` removes it, and the edit tool with `difficulty="hard"` raises `ToolError` matching `difficulty` with the file byte-identical; each fails before the change
- [ ] The new `tests/test_ticket_strategies.py` case finds a drawn text containing `"\ndifficulty: "`, and fails before the change; `make check` passes

## Plan

Add failing MCP and strategy tests first, then expose difficulty on both MCP tools and draw it independently in ticket strategies. Run formatting and checks, commit, and hand off for review.

## History

- 2026-11-26T20:08:38Z zesty-ginger-newt → planning
- 2026-11-26T20:08:50Z zesty-ginger-newt planning → cold-read
- 2026-11-26T20:10:17Z zesty-ginger-newt: changed description
- 2026-11-26T20:10:17Z zesty-ginger-newt cold-read → planning
- 2026-11-26T20:10:20Z zesty-ginger-newt planning → todo
- 2026-11-26T20:10:34Z zesty-ginger-newt: renumbered from TASK-KEGB2N
- 2026-11-27T00:23:23Z jolly-violet-urchin todo → doing
- 2026-11-27T00:26:44Z jolly-violet-urchin: wrote the plan
