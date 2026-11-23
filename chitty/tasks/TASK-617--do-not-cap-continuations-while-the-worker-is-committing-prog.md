---
title: Do not cap continuations while the worker is committing progress
status: backlog
created: 2026-11-23
---

## Description

In taidy TASK-12 (2026-11-23 09:31-09:34 UTC, Chitty 0.7.0, pi with gpt-6.1-terra), the work agent ended every turn after one step but made real progress in each continuation: it committed `d7da20d` (regression tests), `d6dbb02` (implementation) and `d5176a3` (integration fixture and Docker), and added a progress note each time. After `MAX_CONTINUATIONS` (5) the runner raised `TASK-12 was unchanged; only committed changes are visible to chitty run` (`src/chitty/run.py:767`) and set the ticket to `error`, although the branch had advanced by three commits and the ticket file had changed. The cap is meant to stop an idle agent, but it counts productive continuations too.

Suggested fixes:
1. Count only continuations in which the branch HEAD (or the ticket file, apart from the status) did not move. Reset the counter when the agent commits.
2. Reword the error. "Was unchanged" is wrong when the ticket and branch did change: say the status is still `doing` after N continuations that made no progress.
3. Optionally: when the cap is hit after progress, leave the ticket in `doing` for the next run, not `error`, since nothing is broken.

## Notes

Suggestion origin: taidy

Folded in from TASK-613: when a work run ends with the ticket still `doing`, prefer requeueing it over `error`, since nothing is broken.

## History

- 2026-11-23T10:24:13Z witty-russet-gannet → backlog
- 2026-11-23T10:24:14Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:32Z witty-russet-gannet: changed notes
