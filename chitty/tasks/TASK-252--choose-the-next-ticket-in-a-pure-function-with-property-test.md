---
title: Choose the next ticket in a pure function, with property tests
status: backlog
created: 2026-11-10
---

## Description

Selection in `src/chitty/store.py` (`next_action`, `_ticket_action` with `refuse=False`, `_skip_reason`) mixes the decision with reading locks, Git and `main`'s files, so it can only be tested through whole repositories. Several past bugs were wrong picks (TASK-147, TASK-200, TASK-222).

**Change:**

- Gather each ticket's facts first: ID, context, status, priority, owner, archived, locked, and each dependency as done, unfinished or broken (with its message).
- Decide in pure functions over those facts: the skip reason, and the choice given `mode` and `owner`.
- `next_action` and `skip_reason` keep their signatures and behaviour; `ticket_action` (`refuse=True`) is out of scope.

**Properties** (`tests/test_property_next.py`, Hypothesis over lists of ticket facts):

- The choice is never archived, locked, in the `human` context, owned by `human`, outside `mode`'s statuses, or a `todo` with an unfinished or broken dependency. With `owner`, it is owned by that owner; without, it has no owner.
- It is the first eligible ticket by status (`review`, `doing`, `todo`), then priority, then ID, or none when nothing is eligible.
- With no `mode` or `owner`, a ticket has no skip reason exactly when choosing from it alone picks it.

## Acceptance Criteria

- [ ] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [ ] Existing `chitty next`, `chitty list` and `chitty run` tests pass unchanged.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
