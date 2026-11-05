---
title: Let `chitty run` leave owned tickets to their owner
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

The human wants to reserve tickets for a stronger model by setting an owner, such as `chitty edit TASK-1 --owner opus`, and have that model pick them out. `owner` is already free text, but `_ticket_action` in `src/chitty/store.py` only treats the exact value `human` specially, so `chitty run` and `chitty next` still select a ticket owned by `opus`. All owners on active tickets are `human` today, so nothing else changes behaviour.

Add a keyword-only `owner: str | None = None` to `next_action` in `src/chitty/store.py`, and an `--owner` option to `chitty next` and `chitty run`, and to the `next` tool in `src/chitty/mcp.py` if it has an equivalent. `run` in `src/chitty/run.py` passes it through. The rules are:

- With no `--owner`, a `todo` or `doing` ticket with any owner is skipped, and a `review` ticket is still selected unless its owner is `human`. Otherwise work reserved for a stronger model could never be reviewed by `chitty run`.
- With `--owner opus`, only tickets owned by `opus` are candidates, at any of those statuses, with the same order and the same dependency rules. `--owner human` is refused with a `ChittyError`, because agents do not take `human` tickets.
- `chitty run --ticket <ID>` still runs a ticket with any owner other than `human`, and still refuses `human`.

`chitty run` forwards arguments it does not know to the agent, and `--owner` must be taken by `chitty run` whether it comes before or after them, as `--ticket` is. `TASK-186` adds `--mode` to the same two places, so whichever lands second rebases. Update the `owner` row and the selection rules in `PLAN.md`, and `README.md`. Because this changes no guide or `chitty.toml`, no version bump is needed.

Out of scope: choosing a model from the owner, which remains a forwarded argument such as `chitty run --owner opus -- --model <name>`, and clearing the owner when a ticket moves to `review`.

## Acceptance Criteria

- [ ] Tests with tickets owned by `opus` show plain `chitty next` and `chitty run` skipping them at `todo` and `doing`, selecting one at `review`, and still skipping `human` at every status, and fail without the change
- [ ] Tests show `--owner opus` on `chitty next` and `chitty run` selecting only that owner's tickets, whichever side of the forwarded arguments it comes, `--owner human` refused, and `chitty run --ticket` running an `opus` ticket and refusing a `human` one
- [ ] `PLAN.md` and `README.md` describe the rules

## History

- 2026-11-05T18:20:01Z mellow-newt → backlog
