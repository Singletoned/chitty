---
title: Investigate gpt-6-luna work sessions stalling in echonomicon (luna replaced terra, which also had problems)
status: backlog
created: 2026-11-24
---

## Description

Project: echonomicon (/Users/singletoned/src/singletoned/echonomicon). The work runner is 'chitty run --loop --mode work -- --model gpt-6-luna' (chitty.toml work_model = openai-codex/gpt-6-luna, agent_command runs pi in print mode). The owner switched work sessions to gpt-6-luna because gpt-6.1-terra was having problems; luna now has its own, so the fix may belong in the runner or prompts rather than in a model choice.

Symptoms on 2026-11-23/24:
- Sessions stop after little or no work, claim a budget limit ('My available session budget is exhausted.') despite the runner's prompt saying there is none, and issue tool calls with an empty command string.
- When the runner's continuation prompt demands a terminal status, the worker picks 'planning' while its own note says the ticket is actionable and has no defect.
- Some sessions leave uncommitted partial edits; the next runner pre-check (make lint test) then fails on the dirty worktree and reports it as main failing.

Affected tickets and pi session logs (~/.pi/agent/sessions/--Users-singletoned-src-singletoned-echonomicon-.worktrees-task-<n>--/):
- TASK-203: 2 sessions. The 2026-11-24T07-57-23 session ran 'ls', two empty commands, claimed budget exhausted, then set planning with 'Implementation has not started. The ticket is actionable and does not have a discovered defect'.
- TASK-195: 6 sessions. Twice left subscriptions.py, title_keys.py (and cli.py, tests/test_title_keys.py) modified and uncommitted; once moved itself to planning while noting no planning was needed; ticket went to error from the dirty-tree pre-check.
- TASK-197: 1 session. Edited publisher.py and four test files, committed nothing, noted 'Returning to planning is not appropriate: requirements are actionable; continue.' and then set planning.
- TASK-196: 9 sessions. Repeated bounces to planning over a property test the ticket already specified; it was eventually split.
- TASK-202: 3 sessions. Went to blocked because a client-rendered web page showed no price, although the ticket gave the values.

The planner (a Claude Code session) had to discard leftovers and return tickets to todo by hand each time. Earlier related suggestions: 'Runner misreads a worktree with uncommitted partial work as an empty branch', 'Workers leave uncommitted work and move tickets to planning against their own note', 'Work model fakes an exhausted budget and the forced-status prompt sends tickets to planning'. Please compare luna and terra sessions on the same tickets, and consider runner-side guards: reject a planning/blocked move whose note denies a defect, detect empty-command calls and budget claims as a stalled session, and commit or report leftover edits.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-24T22:21:20Z zesty-coral-newt → backlog
- 2026-11-24T22:21:21Z zesty-coral-newt: changed notes
