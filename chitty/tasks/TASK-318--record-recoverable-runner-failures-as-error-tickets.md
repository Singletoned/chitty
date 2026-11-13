---
title: Record recoverable runner failures as error tickets
status: planning
labels:
  - bug
  - runner
created: 2026-11-13
---

## Description

When automated ticket work fails, the failure currently disappears into terminal output and cannot be discovered or handed to a stronger repair agent. Distinguish recoverable automation errors from human-blocked work, preserve the ticket worktree, and use the existing error reporter for failures that cannot be attached safely to a ticket.

## Acceptance Criteria

- [ ] Ticket-scoped runner failures move the ticket to `error`, preserve its branch and worktree, and record the phase, error output, and recovery context in the ticket notes.
- [ ] Normal ticket selection skips `error`; an explicit `chitty run --errors` selects only error tickets and gives the agent a repair-oriented prompt.
- [ ] `chitty list` and `chitty show` expose error tickets and their recovery history, while a repaired ticket can return to the normal review or blocked flow.
- [ ] Failures without a safe ticket handoff invoke the configured `error_reporter` with phase, ticket, mode, worktree, and error context.

## Plan

1. Add `error` to the task status model, selection/display, guides, and status-transition validation; keep `blocked` for human or external prerequisites. 2. Refactor `chitty run` failure boundaries so ticket-scoped recoverable failures write an `error` handoff while preserving the worktree, and global/catastrophic failures continue through `error_reporter` with structured context. 3. Add explicit `chitty run --errors` selection and a repair prompt/agent mode; cover landing, agent, setup/check, and unassignable failure paths with real-file tests. 4. Update runner documentation and run format/check.

## History

- 2026-11-13T18:27:49Z zesty-umber-puffin → planning
- 2026-11-13T18:28:00Z zesty-umber-puffin: wrote the plan
