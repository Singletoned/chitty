---
title: Count cold reads only since the ticket's last title change
status: todo
created: 2026-11-26
provisional: true
---

## Description

### Why

In echonomicon on 2026-11-25, `TASK-235` was cold-read once, split (half moved to a new ticket) and rewritten. Its next `chitty check` warned `3 cold reads; simplify or split instead of another read`, though the ticket had had one read in its new shape. The count in `check` (`src/chitty/check.py`, the `cold_reads = sum(new == "cold-read" for _, new in task.transitions())` line) covers the whole History and never resets, so the warning fires on exactly the tickets that followed its advice to split. Decided (the person, 2026-11-26): count only cold reads since the last title change, because a split almost always renames the ticket.

### Change

Add a pure function `cold_reads_since_retitle(history: str) -> int` in `src/chitty/check.py`, and use it in `check` in place of the current count; the threshold (`MAX_COLD_READS`) and message stay. It reads the History section text line by line:

- A transition line is one `HISTORY_LINE_RE` (`src/chitty/model.py`) fully matches, including old date-only lines; it counts when its `new` is `cold-read`.
- An event line is one `HISTORY_EVENT_RE` fully matches, as `Task.with_history_event` writes it. Split its `action` on `; ` (`HISTORY_ACTION_SEPARATOR`); a part `changed a, b` lists the changed fields, split on `, `. An event with `title` as one of those fields, matched exactly, resets the count to 0. Actor names containing `: ` are out of scope, as for every History reader.

An edit that changes both title and status writes the event line first, then the transition, so a read started in the same edit as a retitle counts.

### Out of scope

Resetting on description rewrites, or a reset option; the other `check` warnings.

## Acceptance Criteria

- [ ] In `tests/test_check_ticket_size.py`, a Hypothesis property test (`@settings(max_examples=examples(N))`) of `cold_reads_since_retitle` draws a list of History entries, each either a transition `- 2026-01-01T00:00:00Z a <old> → <new>` with `<new>` from `cold-read`, `planning` and `todo`, or an event `- 2026-01-01T00:00:00Z a: <actions>` whose actions are drawn from `changed title`, `changed title, description`, `changed description, notes`, `replaced notes` and `replaced notes; changed title, labels`, joined with newlines. The result equals the number of transitions into `cold-read` after the last event whose actions name `title`, or all of them when no event does. Fails without the change, because the function does not exist.
- [ ] Through `check`, a `planning` ticket whose History has 3 transitions into `cold-read`, then the event `changed title, description`, then 1 more transition into `cold-read`, gets no `cold reads;` warning; the same History without the event gets one. Fails without the change for the first case. Regression tests: `TestTicketSizeWarnings.test_limits` passes unchanged. `make check` passes.

## History

- 2026-11-26T10:54:47Z calm-ochre-quail → backlog
- 2026-11-26T10:54:50Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:13Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:13Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:13:33Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:13:33Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:14:31Z calm-ochre-quail: changed description
- 2026-11-26T11:14:31Z calm-ochre-quail cold-read → todo
