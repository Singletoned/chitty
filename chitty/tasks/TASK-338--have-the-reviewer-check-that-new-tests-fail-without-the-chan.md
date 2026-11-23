---
title: Have the reviewer check that new tests fail without the change
status: done
labels:
  - untestable
owner: vivid-ginger-heron
created: 2026-11-16
---

## Description

Missing or weak tests are the main review failure cause (31 `Review failed (tests)` here, 69 in echonomicon). Owner decision 2026-11-22: the runner cannot reliably prove this for a repository in any language, so an agent checks it instead.

Today `src/chitty/roles/work.md` (around line 23) tells the worker to see a regression test fail without the fix and note the result, and `src/chitty/roles/review.md` (around line 56) and `src/chitty/guide-runner.md` (around line 40) say a test criterion passes only with evidence that it fails without the change. Nothing says the reviewer must produce that evidence; a reviewer can accept the worker's note.

Change `src/chitty/roles/review.md`: for each test a criterion needs, the reviewer runs it themselves against the code without the change (for example the branch's new test files on top of the merge base, in a temporary worktree of the reviewer's own, removed afterwards), and records the command and the failure in that criterion's line. A worker's note is not enough. When a test passes without the change, the criterion fails with cause `tests`. Keep it general: the guides reach every repository in any language. Keep `tests/test_guide_word_budget.py` passing (trim elsewhere in the file if needed).

## Plan

Replace the one-sentence test rule in src/chitty/roles/review.md with a bullet: the reviewer runs each needed test without the change themselves (merge base plus the branch's test files, in a temporary worktree of their own, removed afterwards), records command and failure in the criterion line, does not accept the worker's note, and fails the criterion with cause tests when it passes. Note the temporary worktree as the exception to the only-this-worktree rule. Stay under the word budget.

## Notes

From the retro discussion: the worker should see which tests passed without the change. Store that run output in the log from the gitignored check log ticket.

Planning 2026-11-18: agreed with the owner that this proof belongs after the work, before review, and is mechanical. At planning time no tests exist; the planning-side version is the cold-read question "are the tests good", now in `src/chitty/roles/cold-read.md`. `TASK-403`, a duplicate filed the same day, was removed.

Question for the owner (2026-11-22, planner). Two design decisions block planning this, and both change user-visible behaviour in every repository that uses `chitty run`:

1. How does the runner find "the tests added or changed on the branch" in a repository of any language? Proposal: a new optional setting `test_paths` (globs, for example `["tests/**"]`) naming the test files; the runner checks out the merge base, overlays the branch's versions of the changed files matching `test_paths`, and runs the configured `check` there, requiring it to fail. No per-language test discovery: the whole check runs, so "at least one test fails" becomes "the check fails". Without `test_paths` set, the runner skips the proof and says so in the log (not silently).
2. Tickets with no code change (`untestable` ones are already skipped) and tickets whose branch changes no file under `test_paths`: proposal: the runner records `no new tests` in the review prompt, and the reviewer decides, as today.

Is this the shape you want (whole-check failure at the merge base, one setting), or do you want per-test granularity (which needs per-language support)?

Reviewed: the ticket has no numbered criteria, so each line below is one requirement from the Description.
1: pass - `src/chitty/roles/review.md:59-64` adds a bullet: for each test a criterion needs, the reviewer shows it fails without the change themselves, with the merge base plus the branch's new or changed test files in a temporary worktree of their own, removed afterwards.
2: pass - the same bullet says to record the command and the failure in the criterion's line, and that a worker's note is not enough.
3: pass - the same bullet says a test that passes without the change fails the criterion with cause `tests`.
4: pass - the temporary worktree is named as the one exception to the worktree rule at `review.md:10-11`. The wording is general: it names no language, test runner or path.
5: pass - `make check` in the worktree: `1142 passed, 791 subtests passed`, including `tests/test_guide_word_budget.py`. The worker reports 839 of 900 words.
Untestable ticket: no test criterion, so the fail-without-change check does not apply. Nit, not a defect: `review.md:71` ("Do not merge or remove branches or worktrees") sits next to the new "remove that worktree". "Of your own" makes the meaning clear enough. The 2026-11-22 owner question in Notes is stale, as the Summary says.

## Summary

src/chitty/roles/review.md now tells the reviewer to show, themselves, that each test a criterion needs fails without the change (merge base plus the branch's test files, in a temporary worktree of their own, removed afterwards), to record the command and failure in the criterion line, not to accept a worker's note, and to fail the criterion with cause tests when the test passes. The temporary worktree is named as the one exception to the stay-in-this-worktree rule. 839 of 900 words; make check passes (1142 tests). The 2026-11-22 owner question in Notes predates the rescoped description and no longer applies.

## History

- 2026-11-16T09:50:19Z intrepid-coral-raven → backlog
- 2026-11-16T10:00:09Z intrepid-coral-raven: changed notes
- 2026-11-16T10:00:14Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:27Z intrepid-coral-raven backlog → planning
- 2026-11-18T20:36:36Z lively-quartz-crane: changed notes
- 2026-11-22T10:12:06Z friendly-jade-stoat: changed labels, notes
- 2026-11-22T11:13:58Z friendly-jade-stoat: changed title, labels, owner, dependencies, description
- 2026-11-22T11:14:07Z friendly-jade-stoat planning → todo
- 2026-11-23T08:28:05Z vivid-ginger-heron: changed owner
- 2026-11-23T08:28:05Z vivid-ginger-heron todo → doing
- 2026-11-23T08:28:22Z vivid-ginger-heron: wrote the plan
- 2026-11-23T08:31:40Z vivid-ginger-heron: changed summary
- 2026-11-23T08:31:40Z vivid-ginger-heron doing → review
- 2026-11-23T10:19:13Z youthful-bronze-puffin: changed notes
- 2026-11-23T10:19:13Z youthful-bronze-puffin review → done
