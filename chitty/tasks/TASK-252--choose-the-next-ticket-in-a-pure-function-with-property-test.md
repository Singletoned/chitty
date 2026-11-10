---
title: Choose the next ticket in a pure function, with property tests
status: doing
created: 2026-11-10
---

## Description

Selection in `src/chitty/store.py` (`next_action`, `_ticket_action` with `refuse=False`, `_skip_reason`) mixes the decision with reading locks, Git and `main`'s files, so it can only be tested through whole repositories. Several past bugs were wrong picks (TASK-147, TASK-200, TASK-222).

**Change:**

- Gather each ticket's facts: ID, context, status, priority, owner, archived, locked.
- Read dependencies only for a non-archived `todo` ticket that passes the lock, human and owner checks, as today: reading them costs a parse of every task file on `main`. Record each as done, unfinished or broken, with the raw `depends_on` text and the error from `find` or `_dependency_is_done`.
- Decide in pure functions over those facts (a new `src/chitty/selection.py`): the skip reason, and the choice given `mode` and `owner`. Drop checks another rule already covers.
- Keep today's behaviour and messages, including `<ID> depends on <reference>: <error>` for the first broken dependency in `depends_on` order. `chitty list` output must not change.
- `next_action` and `skip_reason` keep their signatures. `ticket_action` (`refuse=True`) keeps its own checks and is otherwise out of scope.

**Properties** (`tests/test_property_next.py`, Hypothesis over lists of ticket facts). Use the tests' own status and priority ranks, not the implementation's:

- The choice is never archived, locked, in the `human` context, owned by `human`, outside `mode`'s statuses, or a `todo` with an unfinished or broken dependency. With `owner`, it is owned by that owner; without, it has no owner.
- It is the first choosable ticket by status (`review`, `doing`, `todo`), then priority, then ID, or none.
- With no `mode` or `owner`, an open (`review`, `doing`, `todo`) non-archived ticket has no skip reason exactly when choosing from it alone picks it.
- `done`, `backlog` and `blocked` tickets have no skip reason.

Bias the generator so most examples have two or more choosable tickets, and shuffle the lists, or the ordering property passes vacuously. Expect about 350 lines, test included.

## Acceptance Criteria

- [ ] The property tests pass, and each fails when its rule is removed from the pure functions (record which removals you tried in a note).
- [ ] Existing `chitty next`, `chitty list` and `chitty run` tests pass unchanged.

## Notes

Possible starting point: `refs/cold-read/TASK-252/2` (`git show refs/cold-read/TASK-252/2:<path>`). It reads dependencies for every `todo` ticket, which made `chitty next` about 40% slower; the ticket now says not to. Check it against the criteria; don't trust it.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
- 2026-11-10T22:20:35Z jolly-heron: changed description
- 2026-11-10T22:34:54Z jolly-heron: replaced notes; changed description
- 2026-11-10T22:34:54Z jolly-heron backlog → todo
- 2026-11-10T22:43:14Z nimble-yellowhammer todo → doing
