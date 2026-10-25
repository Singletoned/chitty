---
title: Make chitty list show active tasks across all contexts
status: done
labels:
  - cli
depends_on:
  - TASK-5
created: 2026-10-25
---

## Description

Plain `chitty list` should show every todo and doing task in every context, but not backlog ideas (TASK-5). It currently shows all non-archived tasks in the default context only, including done. Filtering should be easy: e.g. repeatable -c and -s, and a way to include ideas and done tasks.

## Acceptance Criteria

- [x] Plain chitty list shows todo and doing tasks from every context
- [x] Filtering by context and status is easy, and documented in --help
- [x] backlog and done tasks are hidden unless asked for (e.g. -s backlog, -s done)

## Plan

Change list selection to all configured contexts and todo/doing statuses by default. Make --context repeatable, retain repeatable --status as an explicit override, mirror the API in MCP, and document the active-list behavior.

## Notes

Blocked pending TASK-5: list cannot reliably hide ideas until their representation and configuration are defined.

Unblocked by the TASK-5 decision: backlog is a status, so list hides it by status, not by context name. Implement after TASK-5.

Question: Does --all include hidden statuses, or only archived locations? Answer: it retains its existing archive-location meaning; use repeatable --status to include backlog or done.

Verified: plain list returns todo/doing tasks from every context; explicit repeatable -c and -s filters work, including backlog and done; CLI/MCP parity and make check pass.
