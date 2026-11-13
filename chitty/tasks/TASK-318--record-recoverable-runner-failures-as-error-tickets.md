---
title: Record recoverable runner failures as error tickets
status: blocked
labels:
  - bug
  - runner
created: 2026-11-13
---

## Description

When automated ticket work fails, the failure currently disappears into terminal output and cannot be discovered or handed to a stronger repair agent. Distinguish recoverable automation errors from human-blocked work, preserve the ticket worktree, and use the existing error reporter for failures that cannot be attached safely to a ticket.

## Acceptance Criteria

- [ ] Ticket-scoped failures after a ticket and worktree are resolved—setup, check, agent, or landing failures—move the ticket to `error`, preserve its branch and worktree, and record the phase, full captured error output, and recovery context in its notes.
- [ ] Normal `chitty next` and `chitty run` never select `error`; explicit `chitty run --errors` selects only error tickets, uses a repair-oriented agent prompt, and rejects `--ticket`, `--mode`, and `--owner` combinations.
- [ ] A repair run requires the agent to set a repaired ticket to `review` or a ticket requiring a human decision to `blocked`; any other final status is reported as an error.
- [ ] Failures before a safe ticket handoff, including invalid configuration, dirty main checkout, missing branch, interruption, or failure to write the handoff, leave task state unchanged and invoke `error_reporter` with `phase`, `ticket`, `mode`, `worktree`, and full error output.

## Plan

1. Add `error` to the task status model, validation, selection/display, status transitions, and guides; keep `blocked` for human or external prerequisites. 2. Add a dedicated `--errors` run selection and repair prompt, with explicit option validation and repair result validation. 3. Refactor run failure boundaries so setup, check, agent, and landing failures after ticket/worktree resolution write an error handoff without deleting the worktree or branch; preserve existing behavior for interruptions and unsafe global failures. 4. Pass structured phase/ticket/mode/worktree/error context to `error_reporter`, and add focused real-file tests for each failure class. 5. Update runner documentation and run format/check.

## Notes

Cold read found four ambiguities. Resolved here: recoverable failures are setup/check/agent/landing after ticket and worktree resolution; unsafe failures are reported without changing task state; `--errors` is mutually exclusive with `--ticket`, `--mode`, and `--owner`; repair agents must finish in `review` or `blocked`; reporter context has five fields and full captured output.

Implementation is blocked pending human decomposition. The accepted scope couples a new persisted status and selection rules with a second runner mode, repair-agent status validation, multiple failure-boundary semantics, full output capture, and cross-cutting docs/tests. Delivering only part would leave `error` tickets unable to be safely discovered or recovered. Please split into independently verifiable status/selection, repair-run, and failure-handoff tickets.

## History

- 2026-11-13T18:27:49Z zesty-umber-puffin → planning
- 2026-11-13T18:28:00Z zesty-umber-puffin: wrote the plan
- 2026-11-13T18:29:28Z zesty-umber-puffin: changed acceptance criteria, notes; wrote the plan
- 2026-11-13T18:29:32Z zesty-umber-puffin planning → doing
- 2026-11-13T18:31:46Z witty-silver-urchin: changed notes
- 2026-11-13T18:31:46Z witty-silver-urchin doing → blocked
