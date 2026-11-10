---
title: Choose the next ticket in a pure function, with property tests
status: backlog
created: 2026-11-10
---

## Description

Selection in `src/chitty/store.py` (`next_action`, `_ticket_action` with `refuse=False`, `_skip_reason`) mixes the decision with reading locks, Git and `main`'s files, so it can only be tested through whole repositories. Several past bugs were wrong picks (TASK-147, TASK-200, TASK-222).

**Change:**

- Gather each ticket's facts first: ID, context, status, priority, owner, archived, locked, and, for `todo` tickets only, each dependency as done, unfinished or broken (with the raw `depends_on` text and error message).
- Decide in pure functions over those facts: the skip reason, and the choice given `mode` and `owner`. Put each rule in exactly one place: a ticket is choosable when it is not archived, its status is `review`, `doing` or `todo`, it has no skip reason, and it matches `mode` and `owner`.
- Keep today's behaviour and messages, including `<ID> depends on <reference>: <error>` for the first broken dependency in `depends_on` order, and a malformed reference still failing the whole selection.
- `next_action` and `skip_reason` keep their signatures. `ticket_action` (`refuse=True`) is out of scope.

**Properties** (`tests/test_property_next.py`, Hypothesis over lists of ticket facts):

- The choice is never archived, locked, in the `human` context, owned by `human`, outside `mode`'s statuses, or a `todo` with an unfinished or broken dependency. With `owner`, it is owned by that owner; without, it has no owner.
- It is the first choosable ticket by status (`review`, `doing`, `todo`), then priority, then ID, or none.
- With no `mode` or `owner`, a non-archived `review`, `doing` or `todo` ticket has no skip reason exactly when choosing from it alone picks it.

Bias the generator so most examples have two or more choosable tickets, or the ordering property passes vacuously. The diff is expected to be about 350 lines, test included.

## Acceptance Criteria

- [ ] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [ ] Existing `chitty next`, `chitty list` and `chitty run` tests pass unchanged.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
- 2026-11-10T22:20:35Z jolly-heron: changed description
