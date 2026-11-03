---
title: Add a Pi cold-read mode that can use a different model
status: backlog
priority: medium
depends_on:
  - TASK-109
parent: TASK-106
created: 2026-11-03
---

## Description

The pilot's cold read currently runs as a subagent of the session that wrote the ticket. Consider a stage of its own: `pi --chitty-cold-read TASK-12`, in a fresh session, optionally on a cheaper model closer to the one that will do the work, writing its findings to the ticket and leaving the status unchanged. Its findings would feed the ticket loop in `PLAN.md`.

Suggested by the human, 2026-11-03. Decide after the pilot, from how often subagent cold reads found real gaps and whether the choice of model made a difference. A cold read that shares no conversation context does not need a separate process for independence, since it reviews nothing, so a mode is only worth it if it is cheaper or simpler to run.

## History

- 2026-11-03T16:14:34Z lively-panda → backlog
