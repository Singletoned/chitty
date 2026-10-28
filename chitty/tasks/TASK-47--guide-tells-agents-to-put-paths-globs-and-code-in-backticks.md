---
title: Guide tells agents to put paths, globs and code in backticks
status: done
created: 2026-10-28
---

## Description

An agent wrote the criterion 'static/photos/*.jpg are copied into output/'. The bare * is a CommonMark delimiter that happens to render literally, and the project formatter escaped it as \*. A formatter can't tell a glob is code, so the fix belongs where agents write the text: one line in the managed guide block. Don't auto-wrap tokens. The check warning is a separate ticket (TASK-49).

## Acceptance Criteria

- [x] The guide says: put paths, globs, commands, IDs and code in backticks in titles, descriptions, criteria and notes
- [x] init refreshes existing managed blocks with the new line; tests and README/PLAN.md quotes updated

## Plan

Add the agreed backtick guidance to the managed guide, extend init coverage to verify both new and refreshed blocks contain it, update the quoted guide in PLAN.md, then run make format and make check.

## Notes

Suggestion origin: circuitry

Needs refinement before implementation: decide whether this ticket is limited to mandatory guide wording or also includes the optional `chitty check` warning, and add acceptance criteria for the chosen scope. A warning heuristic needs examples and false-positive expectations.

Decided with the human: guide line only here; the check warning is TASK-49.

Reviewed: inspected the guide and regression coverage in commit `a0bacf9`; `make check` passes.

## Summary

Added the agreed backtick guidance to generated agent instructions, covered initial and refreshed guide blocks, and updated the PLAN.md guide excerpt. Verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → done
