---
title: Learn from tickets that fail review three times
status: backlog
created: 2026-11-19
---

## Description

Three failed reviews means the plan was wrong, and nothing currently captures why, so the next plan repeats it. Evidence from echonomicon on 2026-11-13: TASK-141, TASK-143 and TASK-150 were each escalated after 3 failed reviews, every failure a new, small defect. TASK-141: the ticket never said what export does when an episode artifact is missing (a planning gap). TASK-143: criterion 2 bundled six checks under one "shown by tests", and fixing one (three context segments) broke another (the start-clamp case). TASK-150: criteria said "fails on the current code" without saying how a test must observe the result (an assertion ran after the CliRunner isolated filesystem was gone). Common causes: criteria that say "a test shows X" without saying what the test must observe, and reviewers who report one defect per round instead of all of them. Proposal: when a ticket escalates, require a short retrospective note naming the cause (plan gap, review gap, or worker error) and one lesson. Append each lesson to a file the planning guide tells planners and cold readers to read (for example a project-level `chitty/lessons.md`), so `chitty guide plan` and cold reads check new tickets against it. Also ask reviewers to list every failing criterion in one review, not stop at the first. This replaces an earlier suggestion from the same session that proposed allowing more review rounds, which it withdraws.

## Notes

Suggestion origin: echonomicon

Archived: folded into `TASK-411` (retro on tickets reaching a third failed review).

## History

- 2026-11-19T20:55:23Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:24Z sunny-white-dormouse: changed notes
- 2026-11-19T20:59:05Z sunny-white-dormouse: changed notes
