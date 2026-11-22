---
title: Match `--replace-in-description` across rewrapped whitespace
status: backlog
created: 2026-11-22
---

## Description

chitty wraps Description text when it saves, so a phrase that was written on one line can end up split across lines in the stored file. `chitty edit --replace-in-description OLD NEW` then fails with "OLD must occur exactly once; found 0", and the planner has to grep the task file for the exact line breaks first. This happened in echonomicon on TASK-167 (2026-11-22): the OLD text "Share the cache checks with `read_snapshot` rather than copying them." had been wrapped after "cache". Suggestion: match OLD with any run of whitespace equal to any other run (for example regex-escape OLD and turn whitespace into `\s+`), and still require exactly one match.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-22T13:57:50Z friendly-jade-stoat → backlog
- 2026-11-22T13:57:51Z friendly-jade-stoat: changed notes
