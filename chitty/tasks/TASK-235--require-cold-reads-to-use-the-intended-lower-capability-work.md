---
title: Require cold reads to use the intended lower-capability worker model
status: backlog
created: 2026-11-09
---

## Description

Clarify `chitty guide plan`, `chitty guide cold-read`, and cold-reader agent guidance: a pre-implementation cold read measures whether the intended lesser-capability implementation model can understand and execute a ticket. A stronger model can silently bridge missing requirements, so its successful trial is not evidence that the ticket is ready for a weaker worker. Require the intended worker model or a genuinely comparable lower-capability model. If that model hits a token/usage limit or is unavailable, stop and ask the user how to proceed; never silently substitute a stronger model or promote on that evidence. Evidence: while planning Echonomicon storage tickets, Luna hit a usage limit and the planner substituted Sol, used its trial to promote `TASK-76`, and began another trial. The owner correctly rejected this as defeating the cold-read purpose and requested Luna specifically.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-09T12:03:10Z eager-puffin → backlog
- 2026-11-09T12:03:12Z eager-puffin: changed notes
