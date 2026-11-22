---
title: Extend generated ticket placements to contexts, archiving, dates, decoys and linked checkouts
status: todo
depends_on:
  - TASK-523
created: 2026-11-22
---

## Description

Split from `TASK-523` on 2026-11-22. `TASK-523` generates several tickets in one repository with the placements `a b c d e g h k m`, read from the main checkout, using `tests/ticket_placements.py` unchanged. Still uncovered: both contexts (`tasks` and `human`); tickets archived on `main`; commit dates out of causal order; decoy branches (for `TASK-5`: `task-50`, `TASK-5`, `feature/task-5`); the placements `f` (shared `other` branch), `i` (uncommitted file the next `place` would commit) and `j`, `l` (fast-forward merges after other tickets moved `main`); linked checkout kinds 2 to 5; uncommitted edits. Each needs a builder change to `place` (a context, an archived flag, a date source, a per-ticket `other` branch, a merge that tolerates a moved `main`). Plan one ticket per builder change after `TASK-523` lands.

## History

- 2026-11-22T10:00:30Z friendly-jade-stoat → todo
