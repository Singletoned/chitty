---
title: Record the time and actor on History entries
status: done
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

- [x] Status changes and `archive` write History entries with a UTC timestamp to the second and the actor name
- [x] Existing date-only History entries still parse; `PLAN.md` documents the new entry format
- [x] Each write's CLI output names the actor

## Plan

1. Locate all existing History serialization, parsing, status-transition, and archive writes, then define a single actor-and-UTC formatting path that preserves date-only parsing.
2. Add actor-aware History entries and CLI output for status changes and archive only, with focused regression tests and `PLAN.md` documentation.
3. Run the relevant tests, `make format`, and `make check`; inspect the diff, tick satisfied criteria, and prepare the ticket for independent review.

## Notes

Raised by the human; deferred ('maybe to track who does what, but not yet'). Pairs with the self-review ticket.

Held until agents restart with session identity (HUMAN-5).

Needs a human scope decision before implementation. “Every write” spans normal edits, moves, archive/delete cleanup, imports, inbox pulls and `chitty fix`; the ticket must define which are in scope or be split into independently verifiable tickets.

Created HUMAN-8 to record the required scope decision.

Narrowed and split per `HUMAN-8`; the earlier plan covered the whole scope and was removed.

Reviewed: independent implementation by pi-worker verified. Confirmed UTC-second actor-attributed status/archive History serialization, legacy date-only parsing, actor-bearing CLI output, and PLAN.md documentation. make check passes (188 tests, ruff, pyright).

## Summary

Added UTC-second, actor-attributed History entries for status changes and move-mode archive or restore, while retaining parsing and generation of date-only creation/import entries. CLI status and archive output now names the actor.

Verification: new History regression tests failed before the implementation; `make format` and `make check` pass afterward.

## History

- 2026-10-28 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-02 blocked → todo
- 2026-11-02 todo → doing
- 2026-11-02T08:52:36Z pi-worker doing → review
- 2026-11-02T09:17:24Z pi-reviewer review → done
