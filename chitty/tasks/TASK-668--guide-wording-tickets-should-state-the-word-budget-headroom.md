---
title: Guide-wording tickets should state the word budget headroom
status: backlog
created: 2026-11-24
---

## Description

TASK-608, TASK-615 and TASK-624 (all labelled untestable, 2026-11-23) each asked for added guide text, and all three first failed tests/test_guide_word_budget.py: guide.md had 23 words of room for a requested paragraph of about 50, plan.md had 28 for about 65, and work.md had 30 for about 33. Each worker then had to compress the requested wording, and say so, after a full make check. Suggestion: when a ticket adds text to src/chitty/guide.md or src/chitty/roles/, the planner records the file's current word count and budget from BUDGETS in that test, so the ticket's wording fits or the ticket says to raise the budget.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:31Z zesty-coral-newt → backlog
- 2026-11-24T22:21:32Z zesty-coral-newt: changed notes
