---
title: Let a landing error be retried without re-review
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

In echonomicon, TASK-199 passed review (a gpt-6.1-terra reviewer), then the runner's landing failed: the main checkout had a stray untracked file. It went to `error`. Once the file was gone, nothing could land the ticket without a new review. `chitty edit -s done` refuses with "setting status done requires -s review first". `-s review` runs the check and then records the caller as having worked on the ticket. So the following `-s done --note "Reviewed: ..."` fails with "cannot review this task: moved the task to review; leave the review to another agent", even though the caller changed no code.

Suggestion: when the latest review note is a pass and the error is a landing error, provide a path (for example `chitty run --ticket X` in land-only mode, or `edit -s done` allowed from `error`) that re-runs the rebase, check and fast-forward without a fresh review. Or: a status move to `review` alone should not count as working on the ticket.

## Notes

Suggestion origin: echonomicon

Duplicate of TASK-679 (retry landing a passed review after the main checkout was dirty); its extra detail is recorded there.

## History

- 2026-11-24T22:21:29Z zesty-coral-newt → backlog
- 2026-11-24T22:21:30Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:29Z zesty-coral-newt: changed labels, notes
