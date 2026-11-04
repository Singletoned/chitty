---
title: Teach reviewers the per-criterion verdict
status: backlog
priority: medium
depends_on:
  - TASK-166
  - TASK-142
  - TASK-151
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-166` makes a review verdict need one line per criterion. Reviewers should know that before being refused. In `src/chitty/roles/review.md` and the review part of `src/chitty/guide.md`, replace "list every failure in one note" with the form `<number>: pass - <evidence>` or `<number>: fail - <reason>`, where evidence is the command or test that shows it, and say that a test criterion passes only with evidence that the test fails without the change. `TASK-142` removes the prompt from `src/chitty/integrations/pi/chitty.ts`, and `TASK-151` changes these same lines, so this follows both. The `TASK-109` pilot may later replace the test evidence.

## Acceptance Criteria

- [ ] A test shows `chitty guide review` containing the form, and `README.md` and `src/chitty/guide.md` show it
- [ ] `__version__` is bumped above `main`'s

## History

- 2026-11-04T20:47:41Z mellow-newt → backlog
