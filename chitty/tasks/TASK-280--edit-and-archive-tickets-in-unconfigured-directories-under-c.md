---
title: Edit and archive tickets in unconfigured directories under `chitty/`
status: backlog
depends_on:
  - TASK-266
parent: TASK-262
created: 2026-11-11
---

## Description

- After TASK-266, tickets in a directory under `chitty/` with no configured context can be read but not written: `review_required`, `next_number` and `_set_archived` in `src/chitty/store.py` index `config.contexts` by name and raise.
- Make `chitty edit` (including `-s done`) and `chitty archive` work on them, with the repository default `review`. No new tickets are ever added there.

## History

- 2026-11-11T13:42:18Z vivid-yellowhammer → backlog
