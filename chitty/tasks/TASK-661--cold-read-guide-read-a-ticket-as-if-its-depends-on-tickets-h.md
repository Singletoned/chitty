---
title: "Cold-read guide: read a ticket as if its depends_on tickets have landed"
status: backlog
created: 2026-11-24
---

## Description

2026-11-23, splitting TASK-629 into TASK-629, TASK-649 and TASK-650. All four cold reads of TASK-649 and TASK-650 reported as their top "serious" finding that the dependency (TASK-629) is not on `main`, so the ticket's "fails before the change" baseline does not hold today, even after the Description named the baseline as "`main` with TASK-629 landed" and `depends_on` listed it. The planner had to reject the same finding each round. Proposal: `chitty guide cold-read` says to assume every `depends_on` ticket has landed as its own text describes, and to report only contradictions between the ticket and its dependencies' text, not their absence from `main`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:24Z zesty-coral-newt → backlog
- 2026-11-24T22:21:25Z zesty-coral-newt: changed notes
