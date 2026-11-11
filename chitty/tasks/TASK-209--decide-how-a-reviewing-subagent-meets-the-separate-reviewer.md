---
title: Decide how a reviewing subagent meets the separate-reviewer check
status: backlog
created: 2026-11-06
---

## Description

- A reviewing subagent shares its parent's actor, so the separate-reviewer check refuses its review. Seen in echonomicon `TASK-29` (2026-11-05) and spend-model `TASK-67` (2026-11-06). The only ways through are `--override-review-independence` or an invented `CHITTY_ACTOR`.
- Decided with the human on 2026-11-01: a subagent counts as its parent. Its review is a self-check before `-s review`; only a different session may pass or fail the ticket.
- Requested by echonomicon: a project setting that makes the check warn instead of refuse, still recording the same actor in History.
- Also suggested: give subagents a distinct actor automatically.
- Open: keep the 2026-11-01 decision and only make the guide and the refusal message say "self-check, then `-s review`", or add the setting.

## Notes

Suggestion origin: spend-model

Merged TASK-91 and TASK-183 into this ticket in backlog triage (human approved, 2026-11-11).

## History

- 2026-11-06T13:43:46Z youthful-toad → backlog
- 2026-11-06T13:43:47Z youthful-toad: changed notes
- 2026-11-11T10:18:38Z vivid-yellowhammer: changed title, description, notes
