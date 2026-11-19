---
title: Have the runner prove new tests fail without the change
status: planning
depends_on:
  - TASK-353
created: 2026-11-16
---

## Description

Replaces the cold read implementing pass and the guide rule, repeated in every role guide, that a worker must show a regression test fails without the fix. Missing or weak tests are the main review failure cause (31 `Review failed (tests)` here, 69 in echonomicon). Before review, the runner runs the tests added or changed on the branch against the branch merge base with non-test changes removed, and requires at least one to fail. Design decisions for planning: how to identify the new tests per repository language, and what to do for tickets with no code change.

## Notes

From the retro discussion: the worker should see which tests passed without the change. Store that run output in the log from the gitignored check log ticket.

Planning 2026-11-18: agreed with the owner that this proof belongs after the work, before review, and is mechanical. At planning time no tests exist; the planning-side version is the cold-read question "are the tests good", now in `src/chitty/roles/cold-read.md`. `TASK-403`, a duplicate filed the same day, was removed.

## History

- 2026-11-16T09:50:19Z intrepid-coral-raven → backlog
- 2026-11-16T10:00:09Z intrepid-coral-raven: changed notes
- 2026-11-16T10:00:14Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:27Z intrepid-coral-raven backlog → planning
- 2026-11-18T20:36:36Z lively-quartz-crane: changed notes
