---
title: Let a reviewing agent run under its own actor name
status: backlog
created: 2026-11-06
---

## Description

An agent session that spawns a subagent to review a ticket shares the parent's actor name (here `eager-dormouse`), so `chitty edit ID -s done --note 'Reviewed: ...'` refuses: 'cannot review this task: wrote the plan, ticked acceptance criteria, moved the task to review'. The review then has to be recorded with `--override-review-independence`, which defeats the check. If `CHITTY_ACTOR=<name>` already sets the actor, document it in `chitty guide` (planning/review sections) and in the error message that refuses the review, e.g. 'run the reviewer with CHITTY_ACTOR=<other-name>'. Seen in spend-model, 2026-11-06 (TASK-67).

## Notes

Suggestion origin: spend-model

## History

- 2026-11-06T13:43:46Z youthful-toad → backlog
- 2026-11-06T13:43:47Z youthful-toad: changed notes
