---
title: Cap cold reads and flag tickets that keep growing
status: backlog
created: 2026-11-25
provisional: true
---

## Description

Evidence (echonomicon, 2026-11-24): TASK-133 had 9 cold reads and is back in planning for the second time. TASK-213 has gone doing -> planning 4 times, each over the wording of its "wrong version" steps, never over the feature. Every cold read finds something, because the reader's brief is to find problems. The guide re-triggers a read after any fix that changes what the worker builds. So there is no stopping point: each read adds text, and longer text gives the next reader and worker more to question.

The guide's existing brake ("if a third read still finds serious problems, split") did not fire, because readers 4-9 reported their findings as minor, or got patched anyway.

Suggestion (deterministic, in chitty, not more guide text):
- `chitty check`, or `edit -s todo`, warns when a ticket's history shows more than 3 cold-read transitions, or more than 2 worker returns to planning. It suggests escalating to the owner or a stronger planner instead of another round.
- Warn on description length, as the criterion-count warning already does. TASK-133 has only 2 criteria but about 1,100 words, so the 5-criterion warning never fired.
- The cold-read brief asks readers to label each finding "a reasonable worker would get this wrong" or "an unspecified edge case". Only the first kind blocks `todo`.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-25T22:28:44Z calm-ochre-quail → backlog
- 2026-11-25T22:28:46Z calm-ochre-quail: changed notes
