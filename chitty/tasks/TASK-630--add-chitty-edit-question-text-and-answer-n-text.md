---
title: Add `chitty edit --question TEXT` and `--answer N TEXT`
status: backlog
depends_on:
  - TASK-629
parent: TASK-621
created: 2026-11-23
---

## Description

`chitty edit ID --question TEXT` appends an open question; `--answer N TEXT` ticks question N and records TEXT as its answer, refusing an out-of-range N or an already answered question. Both have `-file` variants like other text options, and the MCP edit tool takes the same fields. Behaviour lives in `store.py`.

## History

- 2026-11-23T10:40:15Z witty-russet-gannet → backlog
