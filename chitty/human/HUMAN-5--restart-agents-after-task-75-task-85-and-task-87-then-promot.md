---
title: Restart agents after TASK-75, TASK-85 and TASK-87, then promote TASK-55 and TASK-57
status: blocked
priority: high
depends_on:
  - TASK-75
  - TASK-85
  - TASK-87
created: 2026-11-01
---

## Description

Pi loads its extensions and settings at startup, and agents read the guide when a session starts. TASK-87 (Pi extension), TASK-85 (worktree guidance) and TASK-75 (session names, Pi `exposeSessionEnvironment`) only take effect after a restart, and once TASK-75 lands, an unrestarted Pi agent has no session identity, so its Chitty writes fail. After restarting, check `chitty whoami` in each harness, then move TASK-55 and TASK-57 to `todo`.

## Notes

Blocked for a human with access to the running agents: restart the affected agent sessions, then verify the updated Chitty setup and promote `TASK-55` and `TASK-57` as described. This agent cannot restart other harness sessions.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → blocked
