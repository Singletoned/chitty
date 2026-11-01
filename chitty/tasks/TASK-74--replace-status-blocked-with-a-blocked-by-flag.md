---
title: Replace status `blocked` with a `blocked_by` flag
status: backlog
depends_on:
  - TASK-82
created: 2026-11-01
---

## Description

`blocked` is a status, so a blocked task loses its place in the flow, stops counting as in progress, and keeps its reason in a note that outlives the block (circuitry `CIRCUIT-84`). Make it a flag instead, like a Kanban blocker sticker: an optional single-line frontmatter field `blocked_by` that says what the blockage is. A long explanation goes in a note, and `blocked_by` cites it (dated notes, TASK-73). The status stays where the work actually is.

With `blocked` and `queued` (TASK-70) as flags, the statuses become a straight line in the direction of travel: `backlog`, `todo`, `doing`, `review`, `done`. Agents pull from the right.

TASK-64's escalation currently sets status `blocked`; it should set `blocked_by` instead.

## Acceptance Criteria

- [ ] `blocked_by` is an optional single-line frontmatter field; `edit --blocked-by TEXT` sets it, `--blocked-by ""` clears it, and `list` and `show` display it beside the status
- [ ] Status `blocked` is removed. `chitty check` reports it, and `chitty fix` moves such a task back to its status before `blocked` (from History) with `blocked_by: "see notes"`
- [ ] Setting and clearing `blocked_by` are recorded in History
- [ ] TASK-64's escalation sets `blocked_by` (citing the escalation note) instead of status `blocked`, and the failed-review count restarts when `blocked_by` is cleared
- [ ] MCP sets, clears and reports `blocked_by` through the shared store code
- [ ] `PLAN.md`, `README.md` and the managed guide describe the flag and the five statuses; `version` is bumped

## History

- 2026-11-01 → backlog
