---
title: Rename status `todo` to `ready`
status: backlog
depends_on:
  - TASK-70
  - TASK-74
  - TASK-82
created: 2026-11-01
---

## Description

Status order is the direction of travel (TASK-70), and Kanban calls the column of refined, free-to-start work "Ready". `ready` says what the status means: refined, no open dependencies, can be pulled. `todo` reads as any unfinished work. Existing files say `todo`, so reading has to accept it (or `chitty fix` rewrites it), and `add`'s default, the guide, `PLAN.md`, `README.md` and MCP change with it. Needs a version bump.

## History

- 2026-11-01 → backlog
