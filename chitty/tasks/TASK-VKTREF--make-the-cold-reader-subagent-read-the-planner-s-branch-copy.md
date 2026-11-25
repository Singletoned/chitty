---
title: Make the cold-reader subagent read the planner's branch copy
status: backlog
created: 2026-11-25
provisional: true
---

## Description

2026-11-24: a planner in `.worktrees/plan-quick-tickets` started the `cold-reader` Claude Code subagent with only the ticket ID, as its definition says. The subagent ran from the main checkout, read the stale `main` copy of TASK-658 (status `backlog`, no criteria), and reported "no Acceptance Criteria" as its top finding. That read was wasted. It is the case TASK-678 describes, from the reader's side. Telling the reader the worktree path and expected status in the prompt fixed it. Suggest: the `cold-reader` agent definition (or `chitty guide cold-read <ID>`) checks that the ticket's status is `cold-read` and stops with a clear message if not, and the plan guide says to pass the worktree when planning on a `plan/` branch.

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:28Z calm-ochre-quail → backlog
- 2026-11-25T22:28:30Z calm-ochre-quail: changed notes
