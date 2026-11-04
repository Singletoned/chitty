---
title: Let one worker and one reviewer run at the same time
status: backlog
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

The human asked for this on 2026-11-04: running one worker and one reviewer together should already be fairly safe, and only `chitty next` stands in the way. It always takes `review` first, then `doing`, then `todo`, so two runs pick the same ticket.

Add `--mode work` and `--mode review` to `chitty next` and `chitty run`. `review` selects only among tickets in `review`, and `work` only among `doing` and `todo`, each in the existing order. The two sets never overlap, so one run of each cannot take the same ticket. With no `--mode`, both behave as they do now. Put the filter in `next_action` in `src/chitty/store.py`, so `run` and `cli.py` stay thin. When nothing matches, the error names the mode, so a person can tell an idle reviewer from a broken one.

Not in scope: two workers or two reviewers, because the claim is not atomic; a loop that waits for tickets; and `--mode` alongside `--ticket` from `TASK-138`, which should be refused if both have landed.

## Acceptance Criteria

- [ ] Tests show `--mode review` and `--mode work` each selecting only their own tickets, in both `chitty next` and `chitty run`, with no `--mode` unchanged and a message naming the mode when nothing matches
- [ ] A test runs a work session and a review session on different tickets with their sessions overlapping, using fake agents that wait for each other, and both report the right status
- [ ] `README.md` and `PLAN.md` describe running one of each

## History

- 2026-11-04T20:15:22Z mellow-newt → backlog
