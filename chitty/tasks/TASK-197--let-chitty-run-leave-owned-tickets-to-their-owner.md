---
title: Let `chitty run` leave owned tickets to their owner
status: backlog
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

The human wants to reserve tickets for a stronger model by setting an owner, such as `chitty edit TASK-1 --owner opus`, and have that model pick them out. `owner` is already free text, but `_ticket_action` in `src/chitty/store.py` only treats the exact value `human` specially, so `chitty run` and `chitty next` still select a ticket owned by `opus`. All owners on this repository's active tickets are `human` today, so nothing changes here. Other repositories may differ, because `src/chitty/import_backlog.py` maps an assignee to `owner`: their tickets with other owners stop being selected by a plain `chitty run`. That is accepted, and `README.md` must say so.

Add a keyword-only `owner: str | None = None` to `next_action` in `src/chitty/store.py`, and an `--owner` option to `chitty next` and `chitty run`, and an `owner` parameter to the `next` tool in `src/chitty/mcp.py`, which is the equivalent of `chitty next`. `run` in `src/chitty/run.py` passes it through. The rules are:

- With no `--owner`, a `todo` or `doing` ticket with any owner is skipped, a ticket with no owner is selected as before, and a `review` ticket is still selected unless its owner is `human`. This is deliberate: an owner reserves the work and not its review, so a plain `chitty run` reviews it with the default agent. The owner stays set, so a failed review returns the ticket to `doing`, where only `chitty run --owner <name>` picks it up again, and the third failed review still sets owner `human`.
- With `--owner opus`, only tickets owned by `opus` are candidates, at any of those statuses, with the same order and the same dependency rules. `--owner human` is refused with a `ChittyError`, because agents do not take `human` tickets, and so is an empty `--owner ""`, which could only ever find nothing.
- `chitty run --ticket <ID>` still runs a ticket with any owner other than `human`, and still refuses `human`. Giving both `--ticket` and `--owner` is refused with a `ChittyError`, because they choose a ticket in two different ways.
- `run` makes all three refusals first, before `_preflight`, `refresh_setup` or `pull_suggestions`, which can commit and change the inbox. `next_action` also refuses `human` and an empty owner, for `chitty next` and MCP.

`chitty run` forwards arguments it does not know to the agent, and `--owner` must be taken by `chitty run` whether it comes before or after them, as `--ticket` is, and anything after a `--` is forwarded, including `--owner`. `TASK-186` adds `--mode` to the same two places, so whichever lands second rebases. Update the `owner` row and the selection rules in `PLAN.md`, and `README.md`. Because this changes no guide or `chitty.toml`, no version bump is needed.

Out of scope: choosing a model from the owner, which remains a forwarded argument such as `chitty run --owner opus -- --model <name>`, and clearing the owner when a ticket moves to `review`.

## Acceptance Criteria

- [ ] `PLAN.md` and `README.md` describe the rules
- [ ] Tests show `--owner opus` on `chitty next` and `chitty run` selecting only that owner's tickets, whichever side of the forwarded arguments it comes, `--owner` after `--` being forwarded, and `--owner human`, `--owner ""` and `--ticket` with `--owner` each refused by `chitty run` with nothing committed
- [ ] Tests with tickets owned by `opus` show plain `chitty next`, and a real `chitty run` with a fake agent, skipping them at `todo` and `doing`, which fail without the change, selecting one at `review`, still selecting tickets with no owner, and still skipping `human` at every status
- [ ] A new test shows `chitty run --ticket` running an `opus` ticket and refusing a `human` one, which already passes and guards against a regression, and a test shows the `next` tool in `src/chitty/mcp.py` taking `owner`

## Notes

Implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-197/1`. The code took about 7 minutes, the tests failed without the fix and passed with it, and `make check` exited 0. Fixed: `--owner` with `--ticket` and an empty owner were unhandled; other repositories may have other owners through `import_backlog.py`, so my claim that nothing changes was too broad; the reservation ending at `review` is now stated as deliberate; the MCP tool is decided rather than conditional; and the `--ticket` clause now needs its own test, which the reader itself left out. It confirmed `next_action` has only three callers. Rejected: clearing the owner at `review`, which is out of scope. Another read follows, since this came back with changes.

Second implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-197/2`. Serious, fixed: `--owner human` was refused only after `refresh_setup` and the inbox pull could change things, so all refusals now come first. Also fixed: a failed review was unhandled, and it now returns to the owner, so "the reservation ends at `review`" became "reserves the work and not its review"; `README.md` was claimed to say something it does not yet; a test through real `chitty run` is required, since `next_action` alone misses option handling; which cases must fail first; and `--owner` after `--`. Rejected: removing the default on `owner`, because `next_action` has callers that want none, and `None` means no filter rather than hiding a mistake. A third read follows.

Third implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-197/3`: nothing serious. 11 of its 12 new tests failed without the change for the right reasons and all passed with it, and `make check` exited 0. Fixed, as clarifications so no further read: unowned tickets must still be selected, which a change skipping all work would otherwise pass; who picks up a ticket returned after a failed review; and that the `--ticket` test already passes. Rejected: refusing `--ticket` with a `human` ticket before preflight, which is today's behaviour and outside this ticket; and owned tickets' dependencies not being checked by a plain run, which skips them anyway and still checks them under `--owner`.

## History

- 2026-11-05T18:20:01Z mellow-newt → backlog
- 2026-11-05T18:28:36Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:28:37Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:39:10Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:39:12Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:39:13Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:48:15Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:48:17Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:48:18Z mellow-newt: changed acceptance criteria, notes
