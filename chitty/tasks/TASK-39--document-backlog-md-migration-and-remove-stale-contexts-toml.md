---
title: Document Backlog.md migration and remove stale contexts.toml references
status: done
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

- [x] No user-facing text describes contexts.toml except the removal warning; PLAN.md's design reflects the inbox
- [x] README has a short 'Migrating from Backlog.md' section: chitty init, chitty import backlog-md, review the report, chitty check, commit, then delete backlog/ (and how unknown statuses, demoted headings and non-task folders are reported)
- [x] The steps in that section are verified by hand on a scratch clone of a real Backlog.md repo

## Plan

Remove stale user-facing contexts.toml guidance while retaining its removal warning. Add the documented Backlog.md migration sequence and verify commands and reporting against a filesystem-backed scratch migration, then run make check.

## Notes

Blocked: no real Backlog.md repository is available under /Users/singletoned/src to perform the required scratch-clone migration. A human needs to provide or identify a real legacy repository clone; then run the documented sequence and record its report.

Waiting for a human-provided real Backlog.md repository clone to complete acceptance criterion 3.

Human manually verified the documented migration sequence against a real Backlog.md repository and reported it passed.

All criteria are met; human migration verification passed.

## Summary

Removed stale contexts.toml guidance and documented the Backlog.md migration. Human verified the documented sequence against a real legacy repository.

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → blocked
- 2026-10-28 blocked → review
- 2026-10-28 review → done
