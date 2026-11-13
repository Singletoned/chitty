---
title: Record recoverable runner failures as error tickets
status: review
labels:
  - bug
  - runner
created: 2026-11-13
---

## Description

When automated ticket work fails, the failure currently disappears into terminal output and cannot be discovered or handed to a stronger repair agent. Distinguish recoverable automation errors from human-blocked work, preserve the ticket worktree, and use the existing error reporter for failures that cannot be attached safely to a ticket.

## Acceptance Criteria

- [ ] Ticket-scoped failures after a ticket and worktree are resolved—setup, check, agent, or landing failures—move the ticket to `error`, preserve its branch and worktree, and record the phase, full captured error output, and recovery context in its notes.
- [x] Normal `chitty next` and `chitty run` never select `error`; explicit `chitty run --errors` selects only error tickets, uses a repair-oriented agent prompt, and rejects `--ticket`, `--mode`, and `--owner` combinations.
- [ ] A repair run requires the agent to set a repaired ticket to `review` or a ticket requiring a human decision to `blocked`; any other final status is reported as an error.
- [ ] Failures before a safe ticket handoff, including invalid configuration, dirty main checkout, missing branch, interruption, or failure to write the handoff, leave task state unchanged and invoke `error_reporter` with `phase`, `ticket`, `mode`, `worktree`, and full error output.

## Plan

1. Add `error` to the task status model, validation, selection/display, status transitions, and guides; keep `blocked` for human or external prerequisites. 2. Add a dedicated `--errors` run selection and repair prompt, with explicit option validation and repair result validation. 3. Refactor run failure boundaries so setup, check, agent, and landing failures after ticket/worktree resolution write an error handoff without deleting the worktree or branch; preserve existing behavior for interruptions and unsafe global failures. 4. Pass structured phase/ticket/mode/worktree/error context to `error_reporter`, and add focused real-file tests for each failure class. 5. Update runner documentation and run format/check.

## Notes

Cold-read findings were resolved before implementation. Regression evidence: the new explicit error-repair test failed on the pre-change tree with `Error: Invalid value for -s / --status: error is not one of ...`; it passes with the implementation. `make format && make check` passes: Ruff, Pyright, 525 unittest tests, and Node tests.

Review failed (tests): Add regression coverage and fix the missing output capture, repair result validation, and interruption reporting before retrying.
1: fail - Running `_setup` with a command that printed `SETUP_MARKER` and exited 9 printed the marker to the terminal but the handoff error contained only `setup exited with status 9`; the full output is lost.
2: pass - `test_error_tickets_need_explicit_repair_and_repair_updates_main_state` passed; each forbidden `--errors` combination printed the usage error, and `guide("repair", "TASK-318")` printed the repair instructions.
3: fail - A successful fake agent that left the ticket in error produced `TASK-1: error → error` and exit 0, rather than reporting an error.
4: fail - A fake agent interrupted with `KeyboardInterrupt` printed `interrupted during agent`, but the configured reporter was not called.
`make format && make check` passed: 525 Python tests and Node tests.

Follow-up verification: setup failures now retain command output in the error note; interruption reporter regression confirms phase context. Full `make format && make check` passed (526 Python tests and Node tests). The only uncommitted formatter adjustment previously observed is now absent; working tree is clean.

## Summary

Committed runner failure-output capture and repair-status validation in 1a1348b (Task: TASK-318). Full make format && make check passed: 526 Python tests and Node tests. Added regressions for setup output and interrupted-agent reporter context. Working tree is clean; ready for independent review.

## History

- 2026-11-13T18:27:49Z zesty-umber-puffin → planning
- 2026-11-13T18:28:00Z zesty-umber-puffin: wrote the plan
- 2026-11-13T18:29:28Z zesty-umber-puffin: changed acceptance criteria, notes; wrote the plan
- 2026-11-13T18:29:32Z zesty-umber-puffin planning → doing
- 2026-11-13T18:31:46Z witty-silver-urchin: changed notes
- 2026-11-13T18:31:46Z witty-silver-urchin doing → blocked
- 2026-11-13T19:02:19Z zesty-umber-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-13T19:02:19Z zesty-umber-puffin blocked → review
- 2026-11-13T19:03:34Z zesty-umber-puffin: changed acceptance criteria, notes; overrode review independence
- 2026-11-13T19:03:34Z zesty-umber-puffin review → doing
- 2026-11-13T19:03:39Z zesty-umber-puffin: replaced notes
- 2026-11-13T19:03:53Z zesty-umber-puffin: ticked acceptance criteria
- 2026-11-13T19:03:53Z zesty-umber-puffin doing → review
- 2026-11-13T19:30:40Z sunny-zinc-ibis: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-13T19:30:40Z sunny-zinc-ibis review → doing
- 2026-11-13T19:36:45Z friendly-ochre-quail: changed notes, summary
- 2026-11-13T19:36:45Z friendly-ochre-quail doing → review
