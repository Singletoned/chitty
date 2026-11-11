---
title: Remove contexts
status: backlog
depends_on:
  - TASK-265
  - TASK-266
parent: TASK-262
created: 2026-11-11
---

## Description

- Split before planning. Replace `[contexts]` with one `prefix`; new tickets go in `chitty/tasks/`, including `BACKLOG-` ones; remove `-c`, `chitty move` and per-context `review` and `random_ids`; `chitty init` stops writing `human` and `backlog`.
- Open: how `chitty init` upgrades an existing `chitty.toml` that has `[contexts]` tables.

## History

- 2026-11-11T11:35:16Z vivid-yellowhammer → backlog
