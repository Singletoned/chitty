---
title: Record the time and actor on History entries
status: todo
priority: high
depends_on:
  - TASK-75
  - HUMAN-5
  - HUMAN-8
created: 2026-10-28
---

## Description

Every change to a ticket should be dated and attributed (decided with the human, 2026-11-01), so that self-review becomes visible (circuitry: one session implemented `CIRCUIT-67`..`72`, then reviewed and passed them). Git cannot tell sessions apart: every session commits as the same user.

Scope per `HUMAN-8`: this ticket adds a UTC timestamp to the second and the actor name (`TASK-75`) to the History entries Chitty already writes: status changes and `archive`. `TASK-99` extends History to the remaining edits and to creation. Parallel branches that both append History conflict on adjacent lines; resolving means keeping both, as today.

## Acceptance Criteria

- [ ] Status changes and `archive` write History entries with a UTC timestamp to the second and the actor name
- [ ] Existing date-only History entries still parse; `PLAN.md` documents the new entry format
- [ ] Each write's CLI output names the actor

## Notes

Raised by the human; deferred ('maybe to track who does what, but not yet'). Pairs with the self-review ticket.

Held until agents restart with session identity (HUMAN-5).

Needs a human scope decision before implementation. “Every write” spans normal edits, moves, archive/delete cleanup, imports, inbox pulls and `chitty fix`; the ticket must define which are in scope or be split into independently verifiable tickets.

Created HUMAN-8 to record the required scope decision.

Narrowed and split per `HUMAN-8`; the earlier plan covered the whole scope and was removed.

## History

- 2026-10-28 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-02 blocked → todo
