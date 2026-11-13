---
title: Define label conventions for review kind and difficulty
status: backlog
labels:
  - needs-discussion
created: 2026-11-01
---

## Description

Tasks need tags such as `@design-review` and `@code-review` (which kind of review a ticket needs) and `@hard` and `@easy` (which model level should take it). Chitty already has a `labels` field (`--add-label`, `--rm-label`), so this is probably conventions plus display and filtering, not a new field: decide whether `@` is part of the stored label or only how labels are shown, which labels are suggested by the guide, and how `chitty list` and `chitty next` filter on them (TASK-76).

## Notes

Planner, 2026-11-12: the `@hard`/`@easy` part is now TASK-308 (a `difficulty` field mapped to agents in config). This ticket keeps the review-kind labels.

## History

- 2026-11-01 → backlog
- 2026-11-11T10:17:05Z vivid-yellowhammer: changed labels
- 2026-11-12T21:44:09Z kind-yellow-vole: changed notes
