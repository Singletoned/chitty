---
title: Teach reviewers the per-criterion verdict
status: doing
priority: medium
depends_on:
  - TASK-166
  - TASK-142
  - TASK-151
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-166` makes a review verdict need one line per criterion. Reviewers should know that before being refused. `TASK-142` removes the prompt from `src/chitty/integrations/pi/chitty.ts`, and `TASK-151` changes these same lines, so this follows both.

In `src/chitty/guide.md`, replace "list every failure in one note". In `src/chitty/roles/review.md`, extend the instruction to write one note in the form `Review failed (<cause>): ...`. Both then say: one note, whether it passes or fails, holds a line for every criterion, `<number>: pass - <evidence>` or `<number>: fail - <reason>`, where evidence is the command or test that shows it, below its `Reviewed:` or `Review failed (<cause>):` first line. A test criterion passes only with evidence that the test fails without the change. The `TASK-109` pilot may later replace that test evidence.

In `README.md`, the example at line 58 gains the verdict lines. `PLAN.md`'s description of review gains a sentence on the form.

## Acceptance Criteria

- [ ] A test shows `chitty guide review` containing the form, and `README.md`, `PLAN.md` and `src/chitty/guide.md` show it
- [x] The ticket branch does not bump `__version__`; version selection happens at release.

## Plan

Fix the README review-note example to pass a real newline rather than literal backslash-n, and add a test that extracts/runs the documented verdict against the validator. Verify it fails before the fix, then format and check.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: my quoted phrase is not in `src/chitty/roles/review.md`, how the lines fit with the failure note's form, and what `README.md` and `PLAN.md` gain.

Added 2026-11-05 from the cold read of `TASK-193`, which edits the same failure-note bullet in `src/chitty/roles/review.md`: keep its rule that a claim about what code does is run first and the note gives what was run and what it printed. Whichever lands second merges the wording.

TASK-224 supersedes the branch-version-bump requirement.

Verified: the guide-review regression test passes; generated chitty guide review contains the verdict form and test-failure evidence requirement; README.md, PLAN.md, and src/chitty/guide.md include the form; src/chitty/roles/review.md preserves the run-output requirement. make format && make check passed (403 Python tests and Node tests). No version change.

Review failed (work): the worktree has uncommitted changes: `PLAN.md`, `README.md`, `src/chitty/guide.md`, `src/chitty/roles/review.md`, `tests/test_guide_review_evidence.py`.

Reviewed: updated review guidance requires a verdict line per criterion, and checks pass.
1: pass - `chitty guide review` contains the verdict format and test-without-change evidence requirement; regression test and README.md, PLAN.md, src/chitty/guide.md contain the required form.
2: pass - src/chitty/__init__.py version unchanged.
Verification: `make format && make check` passed (403 Python tests and Node tests). `chitty fix` completed with pre-existing task-format warnings.

Review failed (work): the worktree has uncommitted changes: `PLAN.md`, `README.md`, `src/chitty/guide.md`, `src/chitty/roles/review.md`, `tests/test_guide_review_evidence.py`.

Verified: `python -m unittest tests.test_guide_review_evidence` passed; `chitty guide review` shows numbered pass/fail lines and test-without-change evidence. README.md, PLAN.md and src/chitty/guide.md show the form. `src/chitty/roles/review.md` preserves run-output instructions. `make format && make check` passed (403 Python tests and Node tests); `git diff --check` passed. No version change. `chitty fix` passed with existing task-format warnings.

Review failed (work): the worktree has uncommitted changes: `PLAN.md`, `README.md`, `src/chitty/guide.md`, `src/chitty/roles/review.md`, `tests/test_guide_review_evidence.py`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Planner committed the work, which earlier sessions had verified but left uncommitted. TASK-282 makes `chitty run` catch that when the work session ends.

Review failed (tests): The README example passes a literal backslash-n in double quotes, not a newline, so it cannot submit a valid review verdict. Use a shell-safe real newline and test the documented command.
1: fail - A throwaway call to `_validate_review_verdict` with the exact README note printed `review verdict lines must match ...; missing 1`. The guide regression passed normally and failed four assertions when the review role was restored to main. `make format && make check` passed with `CHITTY_PI_SESSION_ID` set (488 Python tests and Node tests); without it the existing guide-backticks test failed because Pi session identity was missing.
2: pass - `git diff main...HEAD -- src/chitty/__init__.py` printed no differences.

## Summary

Handoff: per-criterion review verdict guidance, regression coverage, README example and PLAN description are in place. Verification: guide test, generated guide, `make format && make check` (403 Python tests and Node tests), and `git diff --check` passed; no version bump. Follow-ups: none.

## History

- 2026-11-04T20:47:41Z mellow-newt → backlog
- 2026-11-04T20:48:51Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:48:52Z mellow-newt backlog → todo
- 2026-11-05T17:10:25Z mellow-newt: changed notes
- 2026-11-08T13:05:16Z eager-puffin: changed acceptance criteria, notes
- 2026-11-09T09:52:13Z youthful-puffin todo → doing
- 2026-11-09T09:52:39Z youthful-puffin: wrote the plan
- 2026-11-09T09:55:48Z youthful-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-09T09:55:50Z youthful-puffin doing → review
- 2026-11-09T12:30:37Z intrepid-puffin: changed notes
- 2026-11-09T12:30:37Z intrepid-puffin review → doing
- 2026-11-09T12:34:44Z lively-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-09T12:34:46Z lively-zander doing → review
- 2026-11-09T12:37:33Z tidy-falcon: changed notes
- 2026-11-09T12:37:33Z tidy-falcon review → doing
- 2026-11-09T12:41:21Z honest-eel: changed notes, summary; ticked acceptance criteria
- 2026-11-09T12:41:21Z honest-eel doing → review
- 2026-11-09T12:41:40Z plucky-ibis: changed owner, notes
- 2026-11-09T12:41:40Z plucky-ibis review → blocked
- 2026-11-11T15:57:24Z vivid-yellowhammer: changed owner, notes
- 2026-11-11T15:57:24Z vivid-yellowhammer blocked → review
- 2026-11-11T16:01:53Z upbeat-crane: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-11T16:01:53Z upbeat-crane review → doing
- 2026-11-11T16:17:27Z jolly-heron: wrote the plan
