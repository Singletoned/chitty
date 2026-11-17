---
title: Review whether TASK-238 environment clearing is still needed
status: done
depends_on:
  - TASK-238
created: 2026-11-10
---

## Description

TASK-238 makes `chitty run` clear `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` for setup and check commands. The person is fixing their shell environment globally. On or after 2026-11-17, decide whether the code still earns its place (other users likely to hit it?) and, if not, write a ticket to remove it.

## Acceptance Criteria

- [ ] A decision is recorded in a note: keep, or a removal ticket ID.

## Notes

Decision, 2026-11-17: remove. No other users should hit a shell that exports `VIRTUAL_ENV` or `UV_PROJECT_ENVIRONMENT` pointing at a shared environment. Removal ticket: `TASK-365`.

## History

- 2026-11-10T14:15:46Z jolly-heron → todo
- 2026-11-17T17:26:28Z kind-umber-toad: changed notes
- 2026-11-17T17:26:28Z kind-umber-toad todo → done
