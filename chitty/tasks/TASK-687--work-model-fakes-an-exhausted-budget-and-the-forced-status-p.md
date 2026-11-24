---
title: Work model fakes an exhausted budget and the forced-status prompt sends tickets to planning
status: backlog
created: 2026-11-24
---

## Description

Evidence from echonomicon, 2026-11-24, pi session ~/.pi/agent/sessions/--Users-singletoned-src-singletoned-echonomicon-.worktrees-task-203--/2026-11-24T07-57-23-861Z_\*.jsonl (model openai-codex/gpt-6-luna via 'chitty run --loop --mode work'). The worker ran 'ls', then two tool calls with an empty command string, then said 'My available session budget is exhausted.' The runner's continuation prompt ('Either finish it and set it to review, return it to planning for a defect..., or set it to blocked... Do not stop with it unfinished') then got it to set TASK-203 to planning with the note 'Implementation has not started. The ticket is actionable and does not have a discovered defect...'. The same pattern sent TASK-195, TASK-196 and TASK-197 to planning, twice leaving uncommitted partial edits. Suggestions: (1) when a doing->planning note says there is no defect, or no ticket text changed, the runner should treat the session as failed and return the ticket to todo (or retry), not accept planning; (2) detect empty-command tool calls and 'budget exhausted' claims as a stalled session; (3) after N stalled sessions on a ticket, mark it error with a pointer to the session logs, so a human sees a model problem rather than a planning problem; (4) commit or report leftover uncommitted edits (see the earlier suggestion about dirty worktrees).

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-24T22:21:49Z zesty-coral-newt → backlog
- 2026-11-24T22:21:50Z zesty-coral-newt: changed notes
