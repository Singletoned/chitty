---
title: Run the audit weekly
status: backlog
owner: human
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- `make audit` needs something to start it about weekly in the main checkout. Decide what: a launchd job on this machine, Claude Code scheduled routines, or a `chitty run` job (TASK-270's `job_order`) that runs it when the last audit is more than 7 days old.

## History

- 2026-11-11T16:18:28Z vivid-yellowhammer → backlog
