---
title: Require cold reads to use the intended lower-capability worker model
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-09
---

## Description

Clarify `chitty guide plan`, `chitty guide cold-read`, and cold-reader agent guidance: a pre-implementation cold read measures whether the intended lesser-capability implementation model can understand and execute a ticket. A stronger model can silently bridge missing requirements, so its successful trial is not evidence that the ticket is ready for a weaker worker. Require the intended worker model or a genuinely comparable lower-capability model. If that model hits a token/usage limit or is unavailable, stop and ask the user how to proceed; never silently substitute a stronger model or promote on that evidence. Evidence: while planning Echonomicon storage tickets, Luna hit a usage limit and the planner substituted Sol, used its trial to promote `TASK-76`, and began another trial. The owner correctly rejected this as defeating the cold-read purpose and requested Luna specifically.

## Acceptance Criteria

- [ ] A dedicated fail-first guide test shows `chitty guide plan` and `chitty guide cold-read` require the intended worker model or a genuinely comparable lower-capability model, not a silent upgrade to a stronger model.
- [ ] The guides say to stop and ask the user when the intended model is unavailable or hits a usage limit, and not promote based on a stronger substitute; `make check` passes.

## Notes

Suggestion origin: echonomicon

Triage: guide-only gap, not duplicate TASK-125, which considers automation of a separate cold-read mode. The current planning guide says cheap/close to worker, but does not prohibit stronger substitution on model failure. Keep in backlog pending implementing cold read.

Archived in backlog triage (human approved, 2026-11-11): already done or superseded.

## History

- 2026-11-09T12:03:10Z eager-puffin → backlog
- 2026-11-09T12:03:12Z eager-puffin: changed notes
- 2026-11-09T12:04:55Z eager-puffin: changed priority, parent, acceptance criteria, notes
- 2026-11-11T10:16:55Z vivid-yellowhammer: changed notes
- 2026-11-11T10:16:56Z vivid-yellowhammer backlog → archived
