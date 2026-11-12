---
title: Map ticket difficulty to an agent command in config, and use it in `chitty run`
status: backlog
depends_on:
  - TASK-311
parent: TASK-308
created: 2026-11-12
---

## Description

- A `[difficulty]` table maps `low`, `medium` and `high` to names in `[agent_commands]`, so changing which model takes a level is a one-line config edit.
- `chitty run` (and each `--loop` attempt) runs a ticket's work and review with its level's agent. `--agent NAME` overrides. A level with no entry uses `agent_command`.
- Open, from the parent: review at the same level or one higher; what an unset difficulty uses.

## History

- 2026-11-12T21:44:05Z kind-yellow-vole → backlog
