---
title: Cold reads should criticise the acceptance criteria
status: backlog
created: 2026-11-19
---

## Description

Cold readers currently check whether a ticket can be implemented, but not whether its criteria can be met with a weak or wrong test. They should criticise every criterion and call out vague wording such as "shown by tests", "a test shows X" or "fails on the current code" that does not say what the test sets up and what it must observe. Evidence from echonomicon on 2026-11-13: TASK-143 criterion 2 bundled six checks under one "shown by tests", and each fix broke another (three context segments either side, then lost the start-clamp case). TASK-150 criterion 2 said "creates no subscriptions.json" without saying where to check, and the test checked after the CliRunner isolated filesystem had been removed, so it could never fail. Both reached a third failed review. Proposal: in `chitty guide cold-read` and `chitty guide plan`, require the reader to report, for each criterion, any vague phrase, the weakest test that would pass it, and whether it bundles more than one behaviour; the planner fixes or splits each before `todo`.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-19T20:55:36Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:37Z sunny-white-dormouse: changed notes
