---
title: Stop `chitty guide cold-read <ID>` when the ticket is not in `cold-read`
status: backlog
created: 2026-11-25
moved_from: TASK-VKTREF
---

## Description

2026-11-24: a planner in `.worktrees/plan-quick-tickets` started the `cold-reader` Claude Code subagent with only the ticket ID, as its definition says. The subagent ran from the main checkout, read the stale `main` copy of TASK-658 (status `backlog`, no criteria), and reported "no Acceptance Criteria" as its top finding. That read was wasted. It is the case TASK-678 describes, from the reader's side. Telling the reader the worktree path and expected status in the prompt fixed it. Suggest: the `cold-reader` agent definition (or `chitty guide cold-read <ID>`) checks that the ticket's status is `cold-read` and stops with a clear message if not, and the plan guide says to pass the worktree when planning on a `plan/` branch.

## Notes

Suggestion origin: chitty

Triage 2026-11-25: `.claude/agents/cold-reader.md` step 1 tells the reader to work in the main checkout, which causes this on a `plan/` branch. Related: TASK-602 (read tickets from the current branch).

## History

- 2026-11-25T22:28:28Z calm-ochre-quail → backlog
- 2026-11-25T22:28:30Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:23Z calm-ochre-quail: changed title, notes
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-VKTREF
