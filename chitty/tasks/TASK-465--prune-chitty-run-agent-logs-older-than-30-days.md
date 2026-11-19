---
title: Prune `chitty run` agent logs older than 30 days
status: backlog
depends_on:
  - TASK-467
created: 2026-11-19
---

## Description

Follows `TASK-276`, which writes one log per ticket run to `<git common dir>/chitty/run/<ID>-<YYYYMMDDTHHMMSSffffffZ>.log`. Plan once it lands. Agreed direction: at the start of every `chitty run`, with or without `--ticket`, delete `*.log` files directly in that directory whose modification time is more than 30 days old (exactly 30 days is kept); the ticket ID is the name before the final `-<stamp>.log`; skip logs whose ticket is locked (`locks.is_locked` in `src/chitty/locks.py`) and any `.log` whose name does not match; never touch `*.lock`; a failed delete warns on stderr and the run continues. The age check is a pure function of (name, modification time, now, locked IDs) and should get a Hypothesis property.

## History

- 2026-11-19T21:18:54Z sunny-white-dormouse → backlog
- 2026-11-19T21:23:46Z sunny-white-dormouse: changed dependencies
