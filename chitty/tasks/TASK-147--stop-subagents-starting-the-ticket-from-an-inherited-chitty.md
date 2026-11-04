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

In `src/chitty/integrations/pi/chitty.ts`, start a ticket from either flag only when `ctx.mode === "tui"`. `ctx.hasUI` will not do: `pi-subagent` starts its child with `--mode rpc`, where it is true. Put the check around the two flag starts only, not as an early return, because `setPiSessionIdentity` and `latestState` at the top of `session_start` must still run. The `/chitty` command does not pass through this code. The Node tests build a `ctx` with no `mode`, so the flag-start tests need one added. `TASK-136` drops `pi-subagent` from `chitty run` sessions, but this still matters for an agent command that adds it back, and for `pi` started by hand.

Out of scope: changing `pi-subagent`, and whether workers should use subagents at all.

## Acceptance Criteria

- [x] `__version__` is bumped above `main`'s
- [x] A Node test shows both flags sending no prompt in `rpc` mode, with the session identity still set, and starting the ticket in `tui` mode

## Plan

1. Inspect the Pi extension session-start handler and its Node test harness.\n2. Add regression coverage for inherited worker and reviewer flags in UI and non-UI contexts.\n3. Gate automatic ticket start on `ctx.hasUI`, leaving the interactive `/chitty` command path unchanged.\n4. Bump the package version, run focused Node tests and `make check`, then verify the criteria before review.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: my fix would have done nothing, because the child runs in `--mode rpc`, not the `--mode json` I assumed; the runner source confirms it, and `hasUI` is true there. Also the guard's placement and the existing tests.

## History

- 2026-11-04T15:11:29Z mellow-newt → todo
- 2026-11-04T15:15:10Z nimble-eel todo → doing
- 2026-11-04T15:15:47Z nimble-eel: wrote the plan
- 2026-11-04T15:17:28Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T15:20:37Z nimble-eel: ticked acceptance criteria
