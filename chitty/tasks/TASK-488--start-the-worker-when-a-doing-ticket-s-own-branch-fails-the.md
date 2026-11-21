---
title: Start the worker when a `doing` ticket's own branch fails the pre-agent check
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-19 the branch `task-428` held a deadlock in its own new code (`main_checkout_lock` was not re-entrant), so `make check` on that branch never finished. The ticket was sent back to `doing` with the fix described, but `chitty run --mode work` runs `_run_check` (`src/chitty/run.py`) before starting the agent, so the worker who was to fix the bug never started. The work loop hung on that check twice, once for about an hour. With a check timeout (`TASK-450`) the check would fail instead of hanging, but a failed check on a `doing` ticket still records an error rather than letting the worker fix it. Any branch that breaks its own tests therefore locks out its own repair. Proposal: when the pre-agent check fails for a ticket already in `doing` on its own branch, and the failure is new on that branch (`main` passes), start the work agent with the check output as context and the instruction to make the check pass, instead of recording `error`. Keep today's behaviour for `todo` claims and review mode.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:49Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:51Z nimble-umber-gannet: changed notes
