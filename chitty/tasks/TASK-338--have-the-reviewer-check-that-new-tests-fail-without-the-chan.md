---
title: Have the reviewer check that new tests fail without the change
status: planning
labels:
  - untestable
owner: untestable
created: 2026-11-16
---

## Description

Missing or weak tests are the main review failure cause (31 `Review failed (tests)` here, 69 in echonomicon). Owner decision 2026-11-22: the runner cannot reliably prove this for a repository in any language, so an agent checks it instead.

Today `src/chitty/roles/work.md` (around line 23) tells the worker to see a regression test fail without the fix and note the result, and `src/chitty/roles/review.md` (around line 56) and `src/chitty/guide-runner.md` (around line 40) say a test criterion passes only with evidence that it fails without the change. Nothing says the reviewer must produce that evidence; a reviewer can accept the worker's note.

Change `src/chitty/roles/review.md`: for each test a criterion needs, the reviewer runs it themselves against the code without the change (for example the branch's new test files on top of the merge base, in a temporary worktree of the reviewer's own, removed afterwards), and records the command and the failure in that criterion's line. A worker's note is not enough. When a test passes without the change, the criterion fails with cause `tests`. Keep it general: the guides reach every repository in any language. Keep `tests/test_guide_word_budget.py` passing (trim elsewhere in the file if needed).

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
- 2026-11-22T11:13:58Z friendly-jade-stoat: changed title, labels, owner, dependencies, description
