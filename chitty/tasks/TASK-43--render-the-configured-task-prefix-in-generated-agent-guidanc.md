---
title: Render the configured task prefix in generated agent guidance
status: review
created: 2026-10-28
---

## Description

After chitty init --prefix CIRCUIT, the managed AGENTS.md block still says commits should end with 'Task: TASK-N', so git log --grep finds nothing. Render the default context's prefix into the guide (Task: CIRCUIT-N) and say to use the ticket's own prefix, which covers repos whose contexts have different prefixes. init already refreshes the managed block, so re-running init picks up a changed prefix.

## Acceptance Criteria

- [x] The managed guide block shows the default context's prefix in the Task: line and the git log --grep example
- [x] The guide says to use the ticket's own prefix when contexts differ
- [x] Re-running init after the prefix changes updates the block; a repo using TASK gets the same text as today, apart from the new wording
- [x] Tests cover a custom prefix and the refresh; README/PLAN.md updated if they quote the guide

## Plan

Trace guide rendering and init refresh behavior, parameterize the managed guidance with the configured default prefix while retaining a rule for mixed contexts, add custom-prefix and refresh regressions, update quoted documentation, then run formatting and the complete check suite.

## Notes

Suggestion origin: circuitry

Decided with the human: default prefix plus 'use the ticket's own prefix' wording; no per-context listing.

## Summary

Rendered the managed guide with the default context prefix while telling agents to use each ticket’s own prefix in mixed contexts. Added custom-prefix and refresh coverage; updated README and PLAN.md. Verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
