---
title: Repeat cold reads after fixes, and compare decisions with criteria
status: backlog
priority: medium
depends_on:
  - TASK-194
parent: TASK-106
created: 2026-11-05
---

## Description

Second part of the `echonomicon` suggestion in `TASK-194`. Fixes to a ticket are a source of new faults. There, three fixed tickets sampled at random for a second read all had real problems, two making the check command impossible to pass, and later reads found faults the first fixes had introduced, such as a criterion left contradicting an updated description. Here, the second read of the `TASK-190` split on 2026-11-05 found two serious faults. Also there, the first ticket done by the weaker model was correct but left stated decisions untested, because implementers test what criteria name.

Add these bullets to `src/chitty/roles/plan.md`, straight after the bullets on cold reads that `TASK-194` leaves, adjusting only line wrapping:

"Repeat the cold read after fixing a serious finding, until a read finds none: fixes are a source of new faults."

"Compare each decision in the description with the criteria, because workers test what criteria name. Say which test must fail without the fix, because a nearby test may already pass."

Those bullets ship to every repository, so do not name `make`. `src/chitty/roles/plan.md` does not reach `AGENTS.md`, so no `chitty init` or version bump is needed. Whichever of this and `TASK-188` lands second merges the wording.

## History

- 2026-11-05T17:53:54Z mellow-newt → backlog
- 2026-11-05T18:03:37Z mellow-newt: changed description, acceptance criteria
