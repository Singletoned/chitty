---
title: Do not stop `chitty run --loop` when a repair agent leaves a ticket in error
status: backlog
created: 2026-11-19
---

## Description

Seen in echonomicon on 2026-11-19 with `chitty run --loop --errors -- --model gpt-6-luna` (chitty 0.6.1, pi print mode). The repair agent for TASK-161 committed partial work, then ended with "The ticket remains in error pending that work", despite a repair prompt saying not to leave it in `error`. chitty printed `Error: repair agent left TASK-161 in invalid status error; expected review or blocked` and exited 1, so the whole loop stopped and later tickets were not run. Suggestion: when a repair agent leaves an invalid status, have chitty set the ticket to `blocked` with a note (the agent final message plus the branch HEAD), then carry on with the loop. One misbehaving ticket should not halt the queue.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-19T20:55:29Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:30Z sunny-white-dormouse: changed notes
