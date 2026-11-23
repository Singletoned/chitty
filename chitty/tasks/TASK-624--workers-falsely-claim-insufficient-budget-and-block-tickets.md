---
title: Workers falsely claim insufficient budget and block tickets
status: backlog
created: 2026-11-23
---

## Description

Workers on taidy (`pi` with `--model gpt-6.1-terra`, started by `chitty run --mode work`, Chitty 0.6.1) repeatedly moved tickets to `blocked` with notes claiming the session lacked budget or capacity. Those claims were false. The model invented them.

Evidence (pi sessions under `~/.pi/agent/sessions/--Users-singletoned-src-singletoned-taidy-.worktrees-task-12--/`, `task-24`, `task-30`, 2026-11-22 22:19 to 23:04 UTC):
- Every session ended its first turn after 2-3 read-only tool calls, at 11-17 thousand total tokens, saying "I did not implement" or "I couldn't complete TASK-N in this session". It made no edits.
- The reasoning summaries for those turns read "Noting limited capacity", "Waiting on available capacity" and "Assessing implementation time". Nothing in the prompt or the environment mentions a budget.
- The runner then sent its continuation prompt ("Do not stop with it unfinished"), and the worker set `blocked` with notes such as "this worker has insufficient execution budget to implement and verify the required regression, property, and Docker tests" and "this session has insufficient execution capacity".
- This happened 4 times on TASK-12 and once each on TASK-24 and TASK-30, each time on a fresh worker. The same model finishes small echonomicon tickets at 25-30 thousand tokens.

Effect: the false reason gives no actionable obstacle, wastes a planner pass each time, and reads as if the runner were starved of resources.

Suggested fixes:
1. In `chitty guide work` and the run prompt, state that the session has no token or time budget the agent needs to manage, and that budget, capacity, context or time is never a valid reason for `blocked`. Too large for one session goes to `planning` with a proposed split.
2. Have `chitty edit -s blocked` (or the runner after the agent exits) reject or flag a blocked note that cites budget, capacity or context. Instead, continue the agent or requeue the ticket, and record the session's real token use from the agent log in the note.

Related, already sent: "Requeue instead of blocking when a worker blocks on its own budget". This suggestion is about the false claim itself and preventing it at the prompt, not only recovering afterwards.

## Notes

Suggestion origin: taidy

Folded in from TASK-606 (follow-up) and TASK-613: under Chitty 0.7.0 the same TASK-24 ran in one session, but the model still invented a budget limit when it stalled, so the guide and prompt wording is still needed. The runner requeue half of TASK-613 is covered by TASK-617.

## History

- 2026-11-23T10:24:24Z witty-russet-gannet → backlog
- 2026-11-23T10:24:25Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:30Z witty-russet-gannet: changed notes
