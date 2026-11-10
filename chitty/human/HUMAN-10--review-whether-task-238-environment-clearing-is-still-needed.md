---
title: Review whether TASK-238 environment clearing is still needed
status: todo
depends_on:
  - TASK-238
created: 2026-11-10
---

## Description

TASK-238 makes `chitty run` clear `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` for setup and check commands. The person is fixing their shell environment globally. On or after 2026-11-17, decide whether the code still earns its place (other users likely to hit it?) and, if not, write a ticket to remove it.

## Acceptance Criteria

- [ ] A decision is recorded in a note: keep, or a removal ticket ID.

## History

- 2026-11-10T14:15:46Z jolly-heron → todo
