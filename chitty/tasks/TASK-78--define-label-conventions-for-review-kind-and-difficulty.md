---
title: Define label conventions for review kind and difficulty
status: backlog
created: 2026-11-01
---

## Description

Tasks need tags such as `@design-review` and `@code-review` (which kind of review a ticket needs) and `@hard` and `@easy` (which model level should take it). Chitty already has a `labels` field (`--add-label`, `--rm-label`), so this is probably conventions plus display and filtering, not a new field: decide whether `@` is part of the stored label or only how labels are shown, which labels are suggested by the guide, and how `chitty list` and `chitty next` filter on them (TASK-76).

## History

- 2026-11-01 → backlog
