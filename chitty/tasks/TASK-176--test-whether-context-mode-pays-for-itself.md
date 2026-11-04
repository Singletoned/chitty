---
title: Test whether `context-mode` pays for itself
status: backlog
priority: low
owner: human
depends_on:
  - TASK-175
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 7. `context-mode` is 44% of the prompt, and its results cost another 16% of spend, but it may replace larger outputs, which the logs cannot show. The human decided on 2026-11-04 that agents keep it, for keeping large output out of a worker's context; the doc also finds `make check` averages about 320 tokens, which questions that. Run comparable tickets with and without it, using the same model, and compare cost per ticket that passes review. This is the human's to run. Do it after the model trial, so one thing changes at a time.

## Acceptance Criteria

- [ ] A note gives both groups' tickets, cost and review outcomes, what could not be compared, and a recommendation

## History

- 2026-11-04T21:41:11Z mellow-newt → backlog
