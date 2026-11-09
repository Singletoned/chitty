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
- [ ] The ticket branch does not bump `__version__`; version selection happens at release.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: my quoted phrase is not in `src/chitty/roles/review.md`, how the lines fit with the failure note's form, and what `README.md` and `PLAN.md` gain.

Added 2026-11-05 from the cold read of `TASK-193`, which edits the same failure-note bullet in `src/chitty/roles/review.md`: keep its rule that a claim about what code does is run first and the note gives what was run and what it printed. Whichever lands second merges the wording.

TASK-224 supersedes the branch-version-bump requirement.

## History

- 2026-11-04T20:47:41Z mellow-newt → backlog
- 2026-11-04T20:48:51Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:48:52Z mellow-newt backlog → todo
- 2026-11-05T17:10:25Z mellow-newt: changed notes
- 2026-11-08T13:05:16Z eager-puffin: changed acceptance criteria, notes
- 2026-11-09T09:52:13Z youthful-puffin todo → doing
