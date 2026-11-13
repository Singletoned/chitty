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

## History

- 2026-11-13T18:27:49Z zesty-umber-puffin → planning
