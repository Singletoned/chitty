---
title: Set and clear `due` with `chitty add --due` and `chitty edit --due`
status: backlog
depends_on:
  - TASK-626
parent: TASK-619
created: 2026-11-23
---

## Description

`chitty add --due DATE` and `chitty edit --due DATE` set the `due` key added by its dependency; `chitty edit --due ''` removes it, following the `--priority ''` precedent. A malformed date is refused before any write. The MCP add and edit tools take the same field; behaviour lives in `store.py` so the two front ends cannot diverge. `chitty show` prints it.

## History

- 2026-11-23T10:39:57Z witty-russet-gannet → backlog
