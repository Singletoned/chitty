---
title: Upgrade repositories automatically, or block writes until they are upgraded
status: doing
priority: high
created: 2026-11-01
---

## Description

Format and setup changes are applied by two commands, `init` (guide, config) and `fix` (file repairs), and nothing says when to run them. A strict reader also rejects files the moment a newer format arrives. Decided with the human (2026-11-01): either Chitty upgrades a stale repository itself, or it blocks every write until it is upgraded. Proposal: `init` is the single upgrade path and also runs format migrations. When the repository's `chitty_version` is older than the running Chitty, a write with `autocommit = true` first upgrades and commits that as its own commit, then does the write. With autocommit off, writes fail with 'run `chitty init`', so upgrade changes are never mixed into someone's uncommitted work. Reads always work. A Chitty older than the repository's `chitty_version` refuses clearly ('needs Chitty X or later') rather than failing validation. This replaces the 'no Chitty-format migrations in v1' principle in `PLAN.md`, and must land before format changes such as TASK-70 and TASK-74.

## Acceptance Criteria

- [x] `chitty init` applies setup and format migrations, idempotently
- [x] With `autocommit = true`, the first write in a stale repository upgrades it in a separate commit before the write
- [x] With autocommit off, writes in a stale repository fail and say to run `chitty init`; reads still work
- [x] Running a Chitty older than the repository's `chitty_version` fails with the version needed
- [x] `PLAN.md` replaces the no-migrations principle and the init/fix split is documented

## Plan

Trace setup-version warnings and every write path. Make `init` the idempotent setup and migration entry point, gate writes on stale/newer versions according to autocommit, and ensure automatic upgrade is a separate commit before the requested write. Add regression tests for stale reads, blocked non-autocommit writes, automatic upgrade commits, and newer-version errors; then update `PLAN.md` and documentation and run `make check`.

## Notes

Review failed: stale repositories still allow `chitty fix` to modify task files. Reproduced with `chitty_version = "0.0.0"`: `chitty fix` repaired a stale filename and exited 0. Gate `fix` and every other write path, including `import backlog-md` and `Repo.finalize`, through the stale-setup policy, with regression tests.

## Summary

Implemented stale-setup write gating. Non-autocommit repositories now require `chitty init`; autocommit repositories upgrade setup in a separate commit before the requested write; newer setup versions fail clearly. Updated `PLAN.md` and `README.md`; added regression coverage. Verification: `make check` (168 tests passed).

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → doing
