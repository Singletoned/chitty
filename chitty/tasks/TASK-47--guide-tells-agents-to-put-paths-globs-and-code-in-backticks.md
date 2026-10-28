---
title: Guide tells agents to put paths, globs and code in backticks
status: todo
created: 2026-10-28
---

## Description

An agent wrote the criterion 'static/photos/*.jpg are copied into output/'. The bare * is a CommonMark delimiter that happens to render literally, and the project formatter escaped it as \*. A formatter can't tell a glob is code, so the fix belongs where agents write the text: one line in the managed guide block. Don't auto-wrap tokens. The check warning is a separate ticket (TASK-49).

## Acceptance Criteria

- [ ] The guide says: put paths, globs, commands, IDs and code in backticks in titles, descriptions, criteria and notes
- [ ] init refreshes existing managed blocks with the new line; tests and README/PLAN.md quotes updated

## Notes

Suggestion origin: circuitry

Needs refinement before implementation: decide whether this ticket is limited to mandatory guide wording or also includes the optional `chitty check` warning, and add acceptance criteria for the chosen scope. A warning heuristic needs examples and false-positive expectations.

Decided with the human: guide line only here; the check warning is TASK-49.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
