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

- [x] A test shows `chitty guide review` containing the form, and `README.md`, `PLAN.md` and `src/chitty/guide.md` show it
- [x] The ticket branch does not bump `__version__`; version selection happens at release.

## Plan

Update the review guide and role wording to require one numbered pass/fail evidence line per criterion, including test-failure-without-change evidence; add CLI guide coverage, and update the README example and PLAN review description. Preserve existing evidence-reporting rules and verify with make format and make check.

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

## Summary

Handoff: reviewer guidance, role prompt, CLI regression coverage, README example and PLAN description now specify per-criterion verdict lines and test-failure evidence. Verification: `make format && make check` passed (403 Python tests and Node tests); generated `chitty guide review` checked; no version bump. Follow-ups: none.

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
