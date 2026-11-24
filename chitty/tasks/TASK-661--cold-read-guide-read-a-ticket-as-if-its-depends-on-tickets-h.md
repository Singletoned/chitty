---
title: "Cold-read guide: read a ticket as if its `depends_on` tickets have landed"
status: todo
labels:
  - untestable
owner: untestable
created: 2026-11-24
---

## Description

### Why

On 2026-11-23, while TASK-629 was split into TASK-629, TASK-649 and TASK-650, all four cold reads of TASK-649 and TASK-650 gave as their top serious finding that TASK-629 is not on `main`, so "fails before the change" does not hold today. They gave it even after the Description named the baseline as "`main` with TASK-629 landed" and `depends_on` listed TASK-629. The planner rejected the same finding every round, and each round cost a read.

### Change

In `src/chitty/roles/cold-read.md`, add one bullet to the list after "Read the ticket with `chitty show <ID>`...", in about this wording:

- Read the ticket as if every ticket in its `depends_on` has landed as its own text describes. Report contradictions between this ticket and theirs, not their absence from `main`.

This grows the cold-read guide by about 30 words. Nothing is cut, because each wrongly reported finding costs a whole read round, which is far more than 30 words. Keep the advice general: nothing specific to this repository.

### Out of scope

Changing `chitty guide cold-read` to print the dependencies' text, and the planner guide's rule on tickets relying on unfinished work (`src/chitty/roles/plan.md`, "If a ticket's text relies on something an unfinished ticket is building").

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:24Z zesty-coral-newt → backlog
- 2026-11-24T22:21:25Z zesty-coral-newt: changed notes
- 2026-11-24T22:47:44Z zesty-coral-newt: changed title, labels, owner, description
- 2026-11-24T22:47:44Z zesty-coral-newt backlog → todo
