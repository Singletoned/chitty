---
title: Record the time and actor of every ticket change
status: blocked
priority: high
depends_on:
  - TASK-75
  - HUMAN-5
  - HUMAN-8
created: 2026-10-28
---

## Description

Every change to a ticket should be dated and attributed (decided with the human, 2026-11-01). Today History records only the date of status and archive changes, and nothing shows who made them, so self-review is invisible (circuitry: one session implemented `CIRCUIT-67`..`72`, then reviewed and passed them). Git cannot tell sessions apart either: every session commits as the same user.

Record a UTC timestamp to the second and the actor name (TASK-75) on every write: status, flags, fields, ticked criteria, plan, notes, summary. Parallel branches that both append History conflict on adjacent lines; resolving means keeping both, which is the same as today.

## Acceptance Criteria

- [ ] Every write appends a History entry with a UTC timestamp to the second, the actor's name, and what changed (status, flags, fields, ticked criteria, plan, notes, summary)
- [ ] Existing date-only History entries still parse; `PLAN.md` documents the new entry format
- [ ] Each write's CLI output names the actor

## Plan

1. Trace task mutation paths and define one backward-compatible History entry format carrying UTC time, actor, and a change description.
2. Route every write through that recorder and expose the actor in write command output.
3. Add regression coverage for existing history, mutation categories, and CLI output; update `PLAN.md`; then run `make check`.

## Notes

Raised by the human; deferred ('maybe to track who does what, but not yet'). Pairs with the self-review ticket.

Held until agents restart with session identity (HUMAN-5).

Needs a human scope decision before implementation. “Every write” spans normal edits, moves, archive/delete cleanup, imports, inbox pulls and `chitty fix`; the ticket must define which are in scope or be split into independently verifiable tickets.

Created HUMAN-8 to record the required scope decision.

## History

- 2026-10-28 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
