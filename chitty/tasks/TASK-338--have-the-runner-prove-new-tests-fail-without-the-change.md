---
title: Have the runner prove new tests fail without the change
status: planning
labels:
  - question
depends_on:
  - TASK-353
created: 2026-11-16
---

## Description

Replaces the cold read implementing pass and the guide rule, repeated in every role guide, that a worker must show a regression test fails without the fix. Missing or weak tests are the main review failure cause (31 `Review failed (tests)` here, 69 in echonomicon). Before review, the runner runs the tests added or changed on the branch against the branch merge base with non-test changes removed, and requires at least one to fail. Design decisions for planning: how to identify the new tests per repository language, and what to do for tickets with no code change.

## Notes

From the retro discussion: the worker should see which tests passed without the change. Store that run output in the log from the gitignored check log ticket.

Planning 2026-11-18: agreed with the owner that this proof belongs after the work, before review, and is mechanical. At planning time no tests exist; the planning-side version is the cold-read question "are the tests good", now in `src/chitty/roles/cold-read.md`. `TASK-403`, a duplicate filed the same day, was removed.

Question for the owner (2026-11-22, planner). Two design decisions block planning this, and both change user-visible behaviour in every repository that uses `chitty run`:

1. How does the runner find "the tests added or changed on the branch" in a repository of any language? Proposal: a new optional setting `test_paths` (globs, for example `["tests/**"]`) naming the test files; the runner checks out the merge base, overlays the branch's versions of the changed files matching `test_paths`, and runs the configured `check` there, requiring it to fail. No per-language test discovery: the whole check runs, so "at least one test fails" becomes "the check fails". Without `test_paths` set, the runner skips the proof and says so in the log (not silently).
2. Tickets with no code change (`untestable` ones are already skipped) and tickets whose branch changes no file under `test_paths`: proposal: the runner records `no new tests` in the review prompt, and the reviewer decides, as today.

Is this the shape you want (whole-check failure at the merge base, one setting), or do you want per-test granularity (which needs per-language support)?

## History

- 2026-11-16T09:50:19Z intrepid-coral-raven → backlog
- 2026-11-16T10:00:09Z intrepid-coral-raven: changed notes
- 2026-11-16T10:00:14Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:27Z intrepid-coral-raven backlog → planning
- 2026-11-18T20:36:36Z lively-quartz-crane: changed notes
- 2026-11-22T10:12:06Z friendly-jade-stoat: changed labels, notes
