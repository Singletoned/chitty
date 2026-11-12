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
- `chitty run` (and each `--loop` attempt) runs a ticket's work with its level's agent and its review with the next level up, capped at `high`. `--agent NAME` overrides. A level with no entry uses `agent_command`.
- An unset difficulty is `low`.

## History

- 2026-11-12T21:44:05Z kind-yellow-vole → backlog
- 2026-11-12T22:13:16Z kind-yellow-vole: changed description
