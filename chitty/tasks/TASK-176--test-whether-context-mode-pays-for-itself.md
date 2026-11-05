---
title: Test whether `context-mode` pays for itself
status: todo
priority: low
owner: human
depends_on:
  - TASK-175
  - TASK-156
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 7. `context-mode` is 44% of the prompt, and its results cost another 16% of spend, but it may replace larger outputs, which the logs cannot show. The human decided on 2026-11-04 that agents keep it, for keeping large output out of a worker's context; the doc also finds `make check` averages about 320 tokens, which questions that. Run comparable tickets with and without it, using an `[agent_commands]` entry from `TASK-156` that leaves out its `-e` path, because arguments to `chitty run` can only add to the command, and the same model, and compare cost per ticket that passes review. This is the human's to run. Do it after the model trial, so one thing changes at a time.

## Acceptance Criteria

- [ ] A note gives both groups' tickets, cost and review outcomes, what could not be compared, and a recommendation

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: how to run without it.

context-mode was disabled on 2026-11-05, because its package upgrade removed the extension path. Sessions now run without it, so this trial would add it back, using the new path in the package `pi/` directory.

## History

- 2026-11-04T21:41:11Z mellow-newt → backlog
- 2026-11-04T21:44:36Z mellow-newt: changed dependencies, description, notes
- 2026-11-04T21:44:38Z mellow-newt backlog → todo
- 2026-11-05T08:22:58Z mellow-newt: changed notes
