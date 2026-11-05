---
title: Add `--mode` to `chitty next` and `chitty run`
status: done
priority: high
parent: TASK-106
created: 2026-11-05
---

## Description

Add `--mode work` and `--mode review` to `chitty next` and `chitty run`. `review` selects only among tickets in `review`, and `work` only among `doing` and `todo`, each in the existing order. With no `--mode`, both behave as they do now. Put the filter in `next_action` in `src/chitty/store.py`, so `run` and `cli.py` stay thin. Add a keyword-only `mode: Literal["work", "review"] | None = None` to `next_action`, which has many callers that want the default, and a `mode` parameter to `run` in `src/chitty/run.py`, passed from the `--mode` option in `src/chitty/cli.py`. `next_action` already has a local called `mode`, so rename that. `chitty next` does not forward arguments, so it only needs the plain option. `TASK-138` adds a `ticket` parameter to `run`, and whichever lands second rebases. When nothing matches, the error says `no next ticket for --mode review`, which keeps the words tests assert, and names the mode, so a person can tell an idle reviewer from a broken one. It still exits non-zero. Declaring the option means `chitty run` no longer forwards a `--mode` to the agent, and `click.Choice` rejects other values. Leave `src/chitty/mcp.py` on the default. In `next_action`, filter before checking dependencies, so a bad reference on a ticket in the other mode does not stop this run.

Split from `TASK-162` on 2026-11-05 so this can land first: it lets a person choose a reviewer's model today, as in `chitty run --mode review -- --model gpt-5.6-terra`. Running the two modes at the same time is `TASK-162`, which needs `TASK-163` and `TASK-164`, so the documentation says to run them one after the other until it lands.

Not in scope: `--mode` alongside `--ticket` from `TASK-138`, which is refused by whichever of the two lands second.

## Acceptance Criteria

- [x] Tests show `--mode review` and `--mode work` each selecting only their own tickets, in both `chitty next` and `chitty run`, with no `--mode` unchanged, and a message naming the mode when nothing matches
- [x] `README.md` and `PLAN.md` describe the option, and say to run the modes one after the other until `TASK-162` lands

## Plan

1. Add keyword-only `mode` to `next_action`, filtering candidates by status before `_ticket_action` (so dependency checks only run on the selected mode); name the mode in the empty error.
2. Add `mode` to `run` in `run.py`, refusing `mode` with `ticket` as its first step (TASK-138 has landed), and pass it to `next_action`.
3. Add `--mode` as a `click.Choice` to `chitty next` and `chitty run`.
4. Tests first for each, seen failing; then `README.md` and `PLAN.md`.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. No serious faults: it ran click and confirmed `--mode` before or after forwarded arguments, `--mode=review`, and rejection of other values. Fixed: how the option reaches `next_action` and `run`, and the clashing local. Rejected: abbreviations such as `--mo review` being forwarded, which is what forwarding means.

Owner set to human only so chitty run leaves this ticket to this session; cleared when done.

The `mode` local the description mentions was in `_ticket_action`, not `next_action` (it moved when `TASK-138` added `ticket_action`); renamed it to `action_mode` there. `--mode` with `--ticket` is refused as the first step of `run` in `run.py`, so it fails even outside Git.

Reviewed: both criteria verified; tests in tests/test_next.py cover next/run --mode, no-mode unchanged, error naming mode, not forwarded, refused with --ticket; README/PLAN updated; make check passes.

## Summary

Added `--mode work|review` to `chitty next` and `chitty run` (a shared `click.Choice` option in `cli.py`). `next_action` takes keyword-only `mode` and filters by status before `_ticket_action` checks dependencies; the empty error is `no next ticket for --mode MODE`. `run` takes `mode`, refuses it with `ticket` before anything else, and `--mode` is no longer forwarded to the agent. MCP keeps the default. `README.md` and `PLAN.md` describe it and say to run the modes one after the other until `TASK-162`.

Verified: three new tests in `tests/test_next.py` (seen failing first), and `make check` passes (262 Python tests plus Node tests). Follow-up: `TASK-162`.

## History

- 2026-11-05T14:13:49Z mellow-newt → backlog
- 2026-11-05T14:23:08Z mellow-newt: changed description, notes
- 2026-11-05T14:23:09Z mellow-newt backlog → todo
- 2026-11-05T19:11:25Z youthful-toad: changed owner, notes
- 2026-11-05T19:11:42Z youthful-toad: wrote the plan
- 2026-11-05T19:11:42Z youthful-toad todo → doing
- 2026-11-05T19:27:45Z youthful-toad: ticked acceptance criteria
- 2026-11-05T19:27:46Z youthful-toad: changed notes, summary
- 2026-11-05T19:27:46Z youthful-toad doing → review
- 2026-11-05T19:31:21Z youthful-toad: changed owner, notes; overrode review independence
- 2026-11-05T19:31:21Z youthful-toad review → done
