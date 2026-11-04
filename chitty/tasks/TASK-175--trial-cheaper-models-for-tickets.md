---
title: Trial cheaper models for tickets
status: backlog
priority: high
owner: human
depends_on:
  - TASK-149
  - TASK-162
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendation 1, its largest saving: same tokens at `gpt-6.1-terra` cost about 34%, and at `gpt-5.6-luna` 10%, of `gpt-5.6-terra`. The human is also hitting limits on two OpenAI subscriptions. A weaker model may take more calls or fail review more often, so price does not settle it, and limits may not follow price.

First check each model exists for this account with `pi --list-models`, because the doc could not confirm its prices. Run small tickets from the queue with `chitty run --mode work -- --model <model>`, starting with `gpt-6.1-terra`, and keep `chitty run --mode review` on one model throughout, so verdicts are comparable, which is why this needs `TASK-162`. Compare cost per ticket that passes review, summing the usage log's lines for each ticket across both modes, with a similar number of Terra tickets as the baseline. The log holds list prices, not limits, so the human records how each counts against the subscription's limits from the provider's own pages, if that can be seen. Tickets differ, so this gives a rough answer rather than a measurement: say what it can and cannot show. This is the human's to run, and the planning session reads the results. The default model is then the human's decision.

## Acceptance Criteria

- [ ] A note gives each model's tickets, cost, review outcomes and failures per ticket, what could not be compared, and a recommendation

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: `--model` would have applied to reviews too, mixing the model's effect with the reviewer's, so this now uses `--mode`; checking the models exist; and where limits come from. It works mechanically: `chitty run` appends these arguments after `agent_command`.

## History

- 2026-11-04T21:41:10Z mellow-newt → backlog
- 2026-11-04T21:44:33Z mellow-newt: changed dependencies, description, notes
