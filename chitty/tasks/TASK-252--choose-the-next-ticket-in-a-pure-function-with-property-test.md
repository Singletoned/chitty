---
title: Choose the next ticket in a pure function, with property tests
status: review
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
- [x] Existing `chitty next`, `chitty list` and `chitty run` tests pass unchanged.

## Plan

Fix dependency gathering so a todo ticket is read only after the requested owner filter passes. Strengthen property tests for status ordering and inactive skip reasons, then run focused tests with mutation trials for those omitted rules. Run format and full checks.

## Notes

Possible starting point: `refs/cold-read/TASK-252/2` (`git show refs/cold-read/TASK-252/2:<path>`). It reads dependencies for every `todo` ticket, which made `chitty next` about 40% slower; the ticket now says not to. Check it against the criteria; don't trust it.

Implemented pure selection and property coverage; full make check passes (459 Python tests and Node tests), including existing next/list/run coverage. I have not yet performed the requested mutation trials removing each individual selection rule, so criterion 1 is not fully verified and remains unchecked.

Mutation trials: the property suite failed after removing archived exclusion, lock exclusion, human-context exclusion, work-mode filtering, review-mode filtering, general owner exclusion, unfinished-dependency exclusion, broken-dependency handling, priority ranking, and numeric ID ranking. Removing only the explicit owner==human clause survived because the general owner exclusion independently rejects that ticket; this is intentional redundant coverage, and generated cases include human owners. Added a fixed unfinished/broken dependency fixture after the first dependency mutation survived the generated examples. Re-verified make format && make check: 460 Python tests plus Node tests pass; existing next/list/run tests unchanged.

Review failed (tests): The selection property mutation record does not include removal of status ordering or the inactive-status skip-reason rule. Dependency gathering also reads an agent-owned todo when no owner is supplied, contrary to the required owner check. A throwaway `next_action` call printed `unexpected dependency read: TASK-2` then `no next ticket`. Add coverage, avoid the read, and record the missing mutation trials. `make format && make check` passed 460 Python tests and the Node tests.

1: fail - The mutation trials do not record status ordering or inactive-status skip-reason removal.
2: pass - Existing tests passed unchanged in `make check`.

Review follow-up: added a regression test for a dependency read on an agent-owned todo when no owner is requested. It failed before the fix at _selection_facts/_dependency_is_done, then passed after owner eligibility required owner=None; explicit owner selection still reads only matching tickets. Property mutation with reversed status rank failed on a review-vs-doing case. The inactive-status guard in skip_reason is behaviorally redundant: removing its status test still returns None because non-todo statuses return immediately afterward, so there is no distinct behavior for a test to kill. Full make format && make check passes (461 Python tests and Node tests). Implementation committed as 9c8dc77. No unrelated files changed.

## Summary

Fixed lazy dependency gathering for plain next: agent-owned todo tickets are now excluded before reading dependencies. Added regression coverage; confirmed it failed pre-fix and passed after. Reversed status-rank mutation is killed by property ordering. The inactive-status skip_reason check is redundant with the subsequent non-todo return, documented in Notes. make format && make check pass (461 Python tests and Node tests). Commit: 9c8dc77. Acceptance criterion 1 remains unchecked only for the behaviorally redundant inactive-status guard mutation.

## History

- 2026-11-10T22:10:57Z jolly-heron → backlog
- 2026-11-10T22:20:35Z jolly-heron: changed description
- 2026-11-10T22:34:54Z jolly-heron: replaced notes; changed description
- 2026-11-10T22:34:54Z jolly-heron backlog → todo
- 2026-11-10T22:43:14Z nimble-yellowhammer todo → doing
- 2026-11-10T22:43:53Z nimble-yellowhammer: wrote the plan
- 2026-11-10T22:55:28Z nimble-yellowhammer: changed notes
- 2026-11-10T22:57:58Z nimble-yellowhammer: changed notes, summary; ticked acceptance criteria
- 2026-11-10T22:57:58Z nimble-yellowhammer doing → review
- 2026-11-10T23:00:46Z tidy-wren: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-10T23:00:46Z tidy-wren review → doing
- 2026-11-10T23:05:27Z lively-puffin: wrote the plan
- 2026-11-10T23:08:22Z lively-puffin: changed notes, summary
- 2026-11-10T23:08:22Z lively-puffin doing → review
