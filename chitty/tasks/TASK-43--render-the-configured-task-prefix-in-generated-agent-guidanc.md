---
title: Render the configured task prefix in generated agent guidance
status: todo
created: 2026-10-28
---

## Description

After chitty init --prefix CIRCUIT, the managed AGENTS.md block still says commits should end with 'Task: TASK-N', so git log --grep finds nothing. Render the default context's prefix into the guide (Task: CIRCUIT-N) and say to use the ticket's own prefix, which covers repos whose contexts have different prefixes. init already refreshes the managed block, so re-running init picks up a changed prefix.

## Acceptance Criteria

- [ ] The managed guide block shows the default context's prefix in the Task: line and the git log --grep example
- [ ] The guide says to use the ticket's own prefix when contexts differ
- [ ] Re-running init after the prefix changes updates the block; a repo using TASK gets the same text as today, apart from the new wording
- [ ] Tests cover a custom prefix and the refresh; README/PLAN.md updated if they quote the guide

## Notes

Suggestion origin: circuitry

Decided with the human: default prefix plus 'use the ticket's own prefix' wording; no per-context listing.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
