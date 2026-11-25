---
title: Reused worktree dirtied by an earlier session's formatter blocks a finished ticket
status: backlog
created: 2026-11-25
moved_from: TASK-C9HGE5
---

## Description

In echonomicon, TASK-213's work was complete and checks passed, but the worker's move to review was refused because chitty.toml was 'already modified at session start'. The worker then moved the ticket to blocked. The diff was whitespace only: an earlier session ran 'mate check', whose taplo step realigned a trailing comment because main's chitty.toml was not taplo-clean (fixed on main in 9e0793ff). Suggestions: (1) show the dirty diff in the refusal message so the agent can see it is mechanical; (2) when setting up a work session in a reused worktree, report pre-existing tracked changes before the agent starts instead of at handoff.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-25: merged into TASK-676.

## History

- 2026-11-25T22:28:43Z calm-ochre-quail → backlog
- 2026-11-25T22:28:44Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:45Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:47Z calm-ochre-quail backlog → archived
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-C9HGE5
