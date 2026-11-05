---
title: Exit 3 when `chitty next` or `chitty run` has no ticket
status: backlog
priority: high
owner: human
parent: TASK-106
created: 2026-11-05
---

## Description

The human asked on 2026-11-05 for a reviewer or worker loop to wait out an idle queue without treating it as a failure, after `TASK-186` added `--mode`. Today `next_action` in `src/chitty/store.py` raises a plain `ChittyError` when nothing matches, which `_Group.invoke` in `src/chitty/cli.py` turns into exit 1, the same status as a broken setup or an agent that made no progress. The human chose a distinct exit code over exiting 0, because `while chitty run; do :; done` must still stop.

Add `NoNextTicket(ChittyError)` to `src/chitty/errors.py`, raise it from `next_action` with the existing messages (`no next ticket`, `no next ticket for --mode MODE`), and have `_Group.invoke` exit 3 for it, still printing the message to stderr. 3 is free: Click uses 1 and 2, `run` uses 130 for an interrupt, and an agent's own exit status always surfaces as 1 through `ChittyError`. Put the number in a module-level constant. Both `chitty next` and `chitty run` get it, with or without `--mode`. `chitty run --ticket` never raises it, because `ticket_action` refuses with its own errors. The MCP `next` tool still raises a `ToolError` with the same text.

Document the code and an idle loop in `README.md` and `PLAN.md`: `while chitty run --mode review || [ $? -eq 3 ]; do sleep 60; done` runs until something fails, while `while chitty run; do :; done` still stops when the queue is empty.

Out of scope: a `chitty run` that waits for tickets itself, and any other exit code.

## Acceptance Criteria

- [ ] Tests show `chitty next` and `chitty run`, with and without `--mode`, exiting 3 with the existing message when nothing matches, and a failing agent still exiting 1
- [ ] `README.md` and `PLAN.md` document exit 3 and the idle loop

## History

- 2026-11-05T21:13:41Z youthful-toad → backlog
