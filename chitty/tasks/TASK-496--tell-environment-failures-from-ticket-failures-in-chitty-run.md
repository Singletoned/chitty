---
title: Tell environment failures from ticket failures in `chitty run`
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-20 the runner blamed healthy tickets for problems outside them three times. (1) Agent could not start: `--model gpt-6.2-terra` does not exist in Pi, and TASK-384 and TASK-474 went `doing` → `error`. (2) Flaky test on `main`: `tests/test_property_blockers.py` mutant 1 survived about one run in ten, so the pre-session `check` failed and TASK-384 went to `error` with no agent. (3) A landing rebase stopped on a ticket-file conflict and the loop exited, leaving the worktree mid-rebase. Each needed a person or planner agent to diagnose and reset. Suggest the runner classify each failure: ticket failures (the agent ran and the work is wrong, or check fails only on the ticket branch) are recorded on the ticket as today; environment failures (agent exits within seconds with no commits, unknown model, `check` also fails on `main`, a Git operation fails) leave the ticket status unchanged, are reported loudly, and pause the loop until fixed. A cheap discriminator for a failing pre-session check: run the same check on `main` (or reuse a cached result for the current `main` tip); if it fails there too, it is not this ticket. Related narrower suggestions filed the same day: agent start failures, and landing conflicts.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:59Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:01Z nimble-umber-gannet: changed notes
