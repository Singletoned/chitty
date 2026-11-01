---
title: Provide Claude Code and Codex sessions to verify Chitty actor identity
status: todo
priority: high
depends_on:
  - TASK-75
created: 2026-11-01
---

## Description

Once TASK-75 lands, verify Chitty's session names in real sessions: run `chitty whoami` in Claude Code, Codex and Pi (after `chitty init` has set Pi's `exposeSessionEnvironment` and Pi has been restarted). Check that the name survives a compaction and that a subagent gets its parent's name. Record the results on TASK-75, and open a ticket for any harness that fails.

## History

- 2026-11-01 → todo
