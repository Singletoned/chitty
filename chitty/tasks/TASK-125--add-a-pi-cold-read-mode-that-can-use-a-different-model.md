---
title: Add a Pi cold-read mode that can use a different model
status: backlog
priority: low
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

Decided with the human, 2026-11-03, replacing the earlier note about automating this: cold reads stay an informal part of planning sessions, as a subagent, with no tooling or enforcement. This ticket is only for if they need to become their own stage, such as `design-review`. `chitty run` will not gate on them.

Idea from the human, 2026-11-03: if cold reads are automated, one coordinating session could run them across a batch, handle their outcomes and raise questions to the human. Suggested shape: a fresh session per batch or parent ticket with its memory in files, not a long-lived one, and its choices shown at `review-ticket`. Try it by hand first: give a fresh session a planned batch and see whether it finds the cross-ticket problems this planning session found, such as `TASK-122` relying on `ORIG_HEAD` despite the `TASK-120` retry, and the unlanded `task-118` branch.

## History

- 2026-11-03T16:14:34Z lively-panda → backlog
- 2026-11-03T16:16:15Z lively-panda: changed notes
- 2026-11-03T18:18:19Z lively-panda: changed priority, notes
- 2026-11-03T19:23:02Z lively-panda: changed priority, notes
- 2026-11-03T20:18:27Z lively-panda: changed notes
