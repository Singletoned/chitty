---
title: Check the usage log against a real session and document it
status: todo
priority: high
depends_on:
  - TASK-148
parent: TASK-106
created: 2026-11-04
---

## Description

Last part of the log designed in `TASK-127`. Run a real Pi session in a scratch repository and compare its log line with the sum in its session file. A large difference means Pi is not recording some calls, so say what is missing rather than adjusting for it. `PLAN.md` and `README.md` then describe the log and say its costs are list prices.

Out of scope: any report, which is `TASK-111`.

## Acceptance Criteria

- [ ] A note records a real session's log line and session-file sum, and explains any difference
- [ ] `PLAN.md` and `README.md` describe the log and say its costs are list prices

## History

- 2026-11-04T15:11:31Z mellow-newt → todo
