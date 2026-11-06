---
title: Exit 3 when `chitty next` or `chitty run` has no ticket
status: doing
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

The human asked on 2026-11-05 for a reviewer or worker loop to wait out an idle queue without treating it as a failure, after `TASK-186` added `--mode`. Today `next_action` in `src/chitty/store.py` raises a plain `ChittyError` when nothing matches, which `_Group.invoke` in `src/chitty/cli.py` turns into a `click.ClickException` and exit 1, the same status as a broken setup or an agent that made no progress. The human chose a distinct exit code over exiting 0, because `while chitty run; do :; done` must still stop.

Add `NoNextTicket(ChittyError)` and a module-level `NO_NEXT_TICKET_EXIT = 3` to `src/chitty/errors.py`, and raise it from `next_action` with the existing messages (`no next ticket`, `no next ticket for --mode MODE`). `ClickException` always exits 1, so in `_Group.invoke` raise a `ClickException` whose `exit_code` is `NO_NEXT_TICKET_EXIT` for it, keeping the usual `Error: ` line on stderr and nothing on stdout, including with `--json`. An idle queue includes one where every `todo` ticket waits on a dependency. 3 is free: Click uses 1 and 2, `run` uses 130 for an interrupt, and an agent's or setup's own exit status always surfaces as 1 through `ChittyError`, so an agent exiting 3 still makes `chitty run` exit 1. Both `chitty next` and `chitty run` get it, with or without `--mode`. A bad reference still exits 1. `chitty run --ticket` never raises it, because `ticket_action` refuses with its own errors. The MCP `next` tool still raises a `ToolError` with the same text. Change the existing tests that expect exit 1 for an empty queue in place.

Document the code and an idle loop in `README.md` and `PLAN.md`: `while chitty run --mode review || [ $? -eq 3 ]; do sleep 60; done` runs until something fails, while `while chitty run; do :; done` still stops when the queue is empty. Say that `chitty run` checks its configuration, refreshes setup and pulls the inbox before selecting, so each idle pass does those and a broken configuration exits 1, not 3.

Out of scope: a `chitty run` that waits for tickets itself, and any other exit code. No version bump: nothing here reaches repositories through `chitty init`.

## Acceptance Criteria

- [x] `README.md` and `PLAN.md` document exit 3 and the idle loop
- [x] Tests show `chitty next` (also with `--json`) and `chitty run`, with and without `--mode`, exiting 3 with the existing message and no stdout when nothing matches, and an agent exiting 3 still making `chitty run` exit 1

## Plan

1. Change the existing empty-queue tests in `tests/test_next.py` to expect exit 3 and no stdout, add `--json` and an agent exiting 3 (expects 1); see them fail.
2. Add `NoNextTicket` and `NO_NEXT_TICKET_EXIT` to `errors.py`, raise it in `next_action`, map it in `_Group.invoke`.
3. Document exit 3 and the idle loop in `README.md` and `PLAN.md`.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. No wrong claims; it confirmed 3 is unused and that every `except ChittyError` still catches a subclass. Fixed: how to exit 3 when `ClickException` hard-codes 1, where the constant lives, `--json` output, that a dependency-blocked queue counts as idle, that `run`'s preflight, setup refresh and inbox pull happen on every idle pass, editing the existing tests in place, an agent exiting 3 in the criterion, and the version bump (not needed). Rejected: a criterion for the MCP `ToolError`, which an existing test in `tests/test_next.py` already covers.

`PLAN.md` still said to run the two modes one after the other, though `TASK-162` is `done` and its criterion asked to replace that sentence; this change removes it, since it rewrote the same paragraph. `ClickException.exit_code` is a class variable to Pyright, so exit 3 comes from a small subclass, `_NoNextTicketException`, in `cli.py`. Checked with the real binary in a scratch repo: `chitty next --mode review` printed the error and exited 3.

Review failed (tests): the changed empty-queue assertions expect stderr without Click’s required Error: prefix, but _NoNextTicketException correctly preserves the usual ClickException line requested by the ticket. The three affected tests fail: test_next_output_and_empty_queue, test_next_mode_selects_only_its_own_tickets, and test_run_mode_selects_only_its_own_tickets_and_is_not_forwarded. Update their expected stderr and rerun make check.

Changed after the early merge, at the human's report that `Error: no next ticket for --mode work` reads as a failure: the idle message is now a plain stderr line, still exit 3. Not yet on `main`; the reviewer's merge brings it.

## Summary

Implemented exit 3 for idle `chitty next` and `chitty run` selections, including `--json` and mode-specific queues. Idle messages are plain stderr with no stdout; real failures, including agents exiting 3, remain exit 1. MCP behavior is unchanged. Updated `README.md`, `PLAN.md`, and regression coverage. Verified with `make check` (ruff, pyright, 269 unittest cases, and Node tests) plus `chitty fix` (warnings only for pre-existing task prose). Follow-up: none.

## History

- 2026-11-05T21:13:41Z youthful-toad → backlog
- 2026-11-05T21:14:52Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-05T21:14:53Z youthful-toad backlog → todo
- 2026-11-05T21:15:01Z youthful-toad: wrote the plan
- 2026-11-05T21:15:01Z youthful-toad todo → doing
- 2026-11-05T21:20:22Z youthful-toad: ticked acceptance criteria
- 2026-11-05T21:20:23Z youthful-toad: changed owner, notes, summary
- 2026-11-05T21:20:23Z youthful-toad doing → review
- 2026-11-06T09:08:23Z brisk-vole: changed acceptance criteria, notes
- 2026-11-06T09:08:23Z brisk-vole review → doing
- 2026-11-06T09:11:45Z youthful-toad: changed notes
- 2026-11-06T10:16:05Z jolly-raven: ticked acceptance criteria
- 2026-11-06T10:16:14Z jolly-raven: changed summary
