---
title: Document Backlog.md migration and remove stale contexts.toml references
status: todo
labels:
  - docs
depends_on:
  - TASK-36
  - TASK-38
created: 2026-10-27
---

## Description

TASK-29 removed contexts.toml, but README.md (the Contexts paragraph and its example), PLAN.md (user-level contexts section) and add --help (cli.py) still describe it. There is also no step-by-step migration guide; the import is only mentioned in passing.

## Acceptance Criteria

- [ ] No user-facing text describes contexts.toml except the removal warning; PLAN.md's design reflects the inbox
- [ ] README has a short 'Migrating from Backlog.md' section: chitty init, chitty import backlog-md, review the report, chitty check, commit, then delete backlog/ (and how unknown statuses, demoted headings and non-task folders are reported)
- [ ] The steps in that section are verified by hand on a scratch clone of a real Backlog.md repo

## History

- 2026-10-27 → todo
