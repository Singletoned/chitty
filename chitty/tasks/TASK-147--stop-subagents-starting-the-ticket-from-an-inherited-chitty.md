---
title: Stop subagents starting the ticket from an inherited Chitty flag
status: doing
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

Workers and reviewers keep seeing a subagent fail with `Agent is already processing. Specify streamingBehavior`, on `TASK-132` and `TASK-119`. Cause, found on 2026-11-04: `pi-subagent` passes unknown flags on to its child, which I confirmed by calling `parseInheritedCliArgs`, so a child of a `--chitty-review TASK-119` session gets that flag too. The extension's `session_start` handler then sends the ticket's prompt in the child, while the child's own task is starting, and that collision raises the error. It was read from the code, not reproduced end to end.

Beyond the failed subagent, a child may be handling the ticket's prompt, which costs tokens and could touch the ticket.

In `src/chitty/integrations/pi/chitty.ts`, ignore both flags when `ctx.hasUI` is false: a child runs in `--mode json`, and `chitty run` sessions are interactive. Check first that `hasUI` is true in the interactive case, and that the `/chitty` command is unaffected. `TASK-136` drops `pi-subagent` from `chitty run` sessions, but this still matters for an agent command that adds it back, and for `pi` started by hand.

Out of scope: changing `pi-subagent`, and whether workers should use subagents at all.

## Acceptance Criteria

- [ ] A Node test shows both flags ignored with `hasUI` false, with no prompt sent, and still starting the ticket with `hasUI` true
- [ ] `__version__` is bumped above `main`'s

## Plan

1. Inspect the Pi extension session-start handler and its Node test harness.\n2. Add regression coverage for inherited worker and reviewer flags in UI and non-UI contexts.\n3. Gate automatic ticket start on `ctx.hasUI`, leaving the interactive `/chitty` command path unchanged.\n4. Bump the package version, run focused Node tests and `make check`, then verify the criteria before review.

## History

- 2026-11-04T15:11:29Z mellow-newt → todo
- 2026-11-04T15:15:10Z nimble-eel todo → doing
- 2026-11-04T15:15:47Z nimble-eel: wrote the plan
