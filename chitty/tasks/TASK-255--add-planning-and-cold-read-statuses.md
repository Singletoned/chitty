---
title: Add planning and cold-read statuses
status: backlog
labels:
  - plan-next
  - needs-minor
created: 2026-11-11
---

## Description

Add two statuses so ticket writing is visible: `planning` (a ticket being written) and `cold-read` (waiting for a cold read).

- Flow: `backlog` → `planning` → `cold-read` → `planning` → `todo` → `review` → `done`. `doing` and `blocked` are unchanged.
- `STATUSES` in `src/chitty/model.py` becomes `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `review`, `done`. Glyphs and labels: `📝 plan`, `🔎 cold`. Also update the `Literal` types in `model.py` and `src/chitty/mcp.py`.
- `chitty list` and MCP list without a status filter show `planning` and `cold-read` as well as today's four (`src/chitty/cli.py`, `src/chitty/mcp.py`). `backlog` and `done` stay hidden.
- `chitty next` and `chitty run` never pick `planning` or `cold-read` tickets. `src/chitty/selection.py` and `MODE_STATUSES` in `src/chitty/store.py` stay as they are.
- `src/chitty/roles/plan.md`: move a ticket to `planning` while writing it, to `cold-read` while a reader works on it, back to `planning` for the outcomes, then to `todo`.
- Docs: the `status` row in `PLAN.md` "Task file", the pipeline note in "Pipeline and feedback", and the glyph list in `README.md`.

Out of scope:
- Transitions stay unenforced: any status may follow any other, as today.
- Random-ID contexts still allow only `backlog`.
- `chitty run` running cold reads (TASK-259); `queued` and `blocked_by` flags (TASK-70, TASK-74).

Put new tests in `tests/test_statuses_planning.py`. Each fails today, because both statuses are rejected.

## Acceptance Criteria

- [ ] `chitty add -s planning` and `chitty edit -s cold-read` succeed, and MCP edit accepts both statuses.
- [ ] `chitty list` with no `-s` shows a `planning` and a `cold-read` ticket, as `📝 plan` and `🔎 cold`, and still hides `backlog` and `done`; MCP list without a status filter returns the same tickets.
- [ ] With only a `planning` and a `cold-read` ticket, `chitty next` prints `no next ticket`.
- [ ] `chitty guide plan` tells planners to use `-s planning` and `-s cold-read`, and `PLAN.md` and `README.md` list both statuses.

## History

- 2026-11-11T10:02:51Z jolly-heron → backlog
- 2026-11-11T10:18:43Z vivid-yellowhammer: changed description
- 2026-11-11T10:36:54Z vivid-yellowhammer: changed description
- 2026-11-11T10:44:16Z vivid-yellowhammer: changed labels, description, acceptance criteria
