---
title: Say why chitty run --loop skips a ticket in doing or review
status: backlog
created: 2026-11-22
---

## Description

In taidy (2026-11-22), `chitty run --loop --mode review` and `--mode work` sat idle for over 30 minutes while TASK-21 was in `review` and TASK-4 in `doing`, printing nothing about them. Cause: TASK-21 had `owner: claude` (set when an interactive agent took over an errored ticket) and TASK-4 had `owner: human` (set by a reviewer that blocked it), and the runner only picks unowned tickets. Clearing both with `chitty edit ID --owner ""` started a review within 25 seconds. Suggested fix: when the loop finds nothing to do, print one line per skipped ticket in a runnable status with the reason (owned by X, depends on Y), and consider clearing an owner automatically when an interactive agent returns a ticket to `review`.

## Notes

Suggestion origin: taidy

## History

- 2026-11-22T13:57:51Z friendly-jade-stoat → backlog
- 2026-11-22T13:57:52Z friendly-jade-stoat: changed notes
