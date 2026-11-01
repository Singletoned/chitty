---
title: Record the time and actor of every ticket change
status: todo
priority: high
depends_on:
  - TASK-75
created: 2026-10-28
---

## Description

Every change to a ticket should be dated and attributed (decided with the human, 2026-11-01). Today History records only the date of status and archive changes, and nothing shows who made them, so self-review is invisible (circuitry: one session implemented `CIRCUIT-67`..`72`, then reviewed and passed them). Git cannot tell sessions apart either: every session commits as the same user.

Record a UTC timestamp to the second and the actor name (TASK-75) on every write: status, flags, fields, ticked criteria, plan, notes, summary. Parallel branches that both append History conflict on adjacent lines; resolving means keeping both, which is the same as today.

## Acceptance Criteria

- [ ] Every write appends a History entry with a UTC timestamp to the second, the actor's name, and what changed (status, flags, fields, ticked criteria, plan, notes, summary)
- [ ] Existing date-only History entries still parse; `PLAN.md` documents the new entry format
- [ ] Each write's CLI output names the actor

## Notes

Raised by the human; deferred ('maybe to track who does what, but not yet'). Pairs with the self-review ticket.

## History

- 2026-10-28 → backlog
- 2026-11-01 backlog → todo
