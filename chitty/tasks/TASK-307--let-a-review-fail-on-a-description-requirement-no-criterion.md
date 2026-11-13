---
title: Let a review fail on a description requirement no criterion covers
status: backlog
created: 2026-11-12
---

## Description

TASK-289: the reviewer showed a real defect (`chitty run --ticket TASK-1 --mode work` with `error_reporter` set never runs the reporter, although the description says every Chitty error after config load is reported). No criterion covered it, every criterion line was `pass`, and Chitty refused `review -> doing` with `moving review → doing requires at least one fail verdict`, so the reviewer had to block the ticket for a human, who then added criterion 4. The worker had only tested the criteria. Options: allow a `description: fail - <reason>` verdict line that satisfies the gate, or tell reviewers in `chitty guide review` to add the missing criterion and fail it. Either keeps the loop running without a human.

## Notes

Suggestion origin: chitty

## History

- 2026-11-12T21:43:31Z kind-yellow-vole → backlog
- 2026-11-12T21:43:32Z kind-yellow-vole: changed notes
