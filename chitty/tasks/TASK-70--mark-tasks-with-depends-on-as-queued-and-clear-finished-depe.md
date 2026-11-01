---
title: Mark tasks with `depends_on` as queued, and clear finished dependencies automatically
status: backlog
depends_on:
  - TASK-82
created: 2026-11-01
---

## Description

A task with a `depends_on` entry is queued: it cannot start until the tasks in front of it are done. The flag is derived from the field and never stored, so it cannot go stale; Chitty keeps the field current, so agents never have to.

Replaces the earlier design of a stored `waiting` status (decided with the human, 2026-11-01). The name must say "blocked by another ticket", not just "waiting"; `queued` is the working name (a queue is things blocked by the thing in front). It is display and filter only, never typed into files. Its emoji (TASK-72) must read as blocked.

Origin (circuitry, 2026-11-01): `CIRCUIT-84` had `depends_on: CIRCUIT-82` and status `blocked`, and stayed blocked after `CIRCUIT-82` was done, with a stale note. Parents are out of scope: `parent` is grouping only; a parent that should wait on its children lists them in `depends_on`.

## Acceptance Criteria

- [ ] `chitty list` and `show` mark a task with `depends_on` as queued and name the tasks it is queued behind; `--json` includes the flag
- [ ] When a task becomes `done`, is archived, or is deleted, Chitty removes it from every other task's `depends_on`, adds a note to each naming the finished task, and the CLI prints the IDs that are no longer queued
- [ ] `add` and `edit` refuse a `depends_on` entry that is already done
- [ ] `chitty check` warns about a `depends_on` entry pointing at a done task (left by a merge or hand edit), and `chitty fix` removes it with the same note
- [ ] MCP applies and reports the same behaviour through the shared store code
- [ ] `PLAN.md`, `README.md` and the managed guide (do not start queued tasks; use `depends_on`, not `blocked`, for waits on other tickets) are updated; `version` is bumped

## Notes

Suggestion origin: circuitry

Decided with the human: `STATUSES` order is the direction tickets move in, and agents pick the rightmost workable ticket (finish before starting). `blocked` and `waiting` sit where the human placed them; History records where a task really was. A later rename of `todo` to `ready` is likely but not part of this ticket.

Redesigned with the human: `queued` is a flag derived from `depends_on`, not a stored `waiting` status, and `blocked` becomes a `blocked_by` flag (TASK-74). The status-order decision still holds: statuses run in the direction of travel and work is pulled from the right. Back to `backlog` until the flag name is settled.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → backlog
