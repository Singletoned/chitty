---
title: Trial cheaper models for tickets
status: backlog
priority: high
owner: human
depends_on:
  - TASK-149
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 1, its largest saving: same tokens at `gpt-6.1-terra` cost about 34%, and at `gpt-5.6-luna` 10%, of `gpt-5.6-terra`. The human is also hitting limits on two OpenAI subscriptions. A weaker model may take more calls or fail review more often, so price does not settle it, and limits may not follow price.

Run small tickets from the queue on each model with `chitty run -- --model <model>`, starting with `gpt-6.1-terra`, and compare cost per ticket that passes review, using the usage log, with a similar number of Terra tickets as the baseline. A reviewer stays on one model throughout, so verdicts are comparable. Record how each counts against the subscription's limits, if that can be seen. Tickets differ, so this gives a rough answer rather than a measurement: say what it can and cannot show. This is the human's to run, and the planning session reads the results. The default model is then the human's decision.

## Acceptance Criteria

- [ ] A note gives each model's tickets, cost, review outcomes and failures per ticket, what could not be compared, and a recommendation

## History

- 2026-11-04T21:41:10Z mellow-newt → backlog
