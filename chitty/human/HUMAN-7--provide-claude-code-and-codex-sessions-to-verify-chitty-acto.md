---
title: Provide Claude Code and Codex sessions to verify Chitty actor identity
status: blocked
priority: high
depends_on:
  - TASK-75
created: 2026-11-01
---

## Description

Once TASK-75 lands, verify Chitty's session names in real sessions: run `chitty whoami` in Claude Code, Codex and Pi (after `chitty init` has set Pi's `exposeSessionEnvironment` and Pi has been restarted). Check that the name survives a compaction and that a subagent gets its parent's name. Record the results on TASK-75, and open a ticket for any harness that fails.

## Notes

Blocked for a human who can open Claude Code and Codex sessions: run the required identity checks after compaction and for subagents, then record the results on `TASK-75`. This Pi session cannot create or inspect those external harness sessions.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → blocked
