---
title: Add a Pi cold-read mode that can use a different model
status: backlog
priority: high
depends_on:
  - TASK-109
parent: TASK-106
created: 2026-11-03
---

## Description

The pilot's cold read currently runs as a subagent of the session that wrote the ticket. Consider a stage of its own: `pi --chitty-cold-read TASK-12`, in a fresh session, optionally on a cheaper model closer to the one that will do the work, writing its findings to the ticket and leaving the status unchanged. Its findings would feed the ticket loop in `PLAN.md`.

Suggested by the human, 2026-11-03. Decide after the pilot, from how often subagent cold reads found real gaps and whether the choice of model made a difference. A cold read that shares no conversation context does not need a separate process for independence, since it reviews nothing, so a mode is only worth it if it is cheaper or simpler to run.

## Notes

First data point, `TASK-124`: a Sonnet subagent cold read found 9 changes worth adopting and 3 missing criteria, after the author had re-read the ticket and added 2 criteria. The worth of those changes is untested until the ticket is worked and reviewed.

Decided with the human, 2026-11-03: cold reads are now the default for every ticket, done by hand as a subagent or fresh session. So this is no longer a question of whether, only of automating it. Data so far: `TASK-124`, `TASK-126` and `TASK-120` each had real gaps found. `TASK-105` passed first time without one, but it was small and had just been rewritten with the human, so a cold read is not always what makes the difference.

## History

- 2026-11-03T16:14:34Z lively-panda → backlog
- 2026-11-03T16:16:15Z lively-panda: changed notes
- 2026-11-03T18:18:19Z lively-panda: changed priority, notes
