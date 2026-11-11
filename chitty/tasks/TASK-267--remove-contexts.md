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
- `chitty init` leaves existing `[contexts]` tables alone, and Chitty ignores them once contexts are removed. Cleaning them up is decided afterwards.

## History

- 2026-11-11T11:35:16Z vivid-yellowhammer → backlog
- 2026-11-11T11:39:08Z vivid-yellowhammer: changed description
