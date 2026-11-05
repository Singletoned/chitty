---
title: Check whether a conflict-resolved merge hides a ticket
status: backlog
priority: low
parent: TASK-106
created: 2026-11-05
---

## Description

Raised by the cold read of `TASK-184` on 2026-11-05, reasoned from the code and not reproduced. `git log --name-only` prints nothing for a merge commit, so a ticket whose latest blob comes from a conflict-resolved merge matches no listed commit's blob, and `historical_files` in `src/chitty/git.py` may skip it silently. Reproduce it before deciding anything.

## History

- 2026-11-05T12:06:16Z mellow-newt → backlog
