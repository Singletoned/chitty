---
title: Upgrade repositories automatically, or block writes until they are upgraded
status: done
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

Trace every mutation entry point missed by the stale-setup gate, especially `fix`, import, and formatter finalization. Route them through the same autocommit/non-autocommit upgrade policy, add regression tests for each path, run `make check`, and return the ticket to review.

## Notes

Review failed: stale repositories still allow `chitty fix` to modify task files. Reproduced with `chitty_version = "0.0.0"`: `chitty fix` repaired a stale filename and exited 0. Gate `fix` and every other write path, including `import backlog-md` and `Repo.finalize`, through the stale-setup policy, with regression tests.

Resuming after review failure: I will gate `fix`, import, and `Repo.finalize` under the stale-setup policy with regression coverage.

Addressed review failure by applying the shared stale-setup guard to `fix`, import, and batched finalization. Added a regression test proving stale non-autocommit `fix` cannot rename task files. Verified with focused tests and `make check`.

Reviewed: independent follow-up in e19a27a gates `fix`, import, and batched finalization through the setup policy. Reproduced stale non-autocommit `chitty fix`: it now exits non-zero, leaves the file unchanged, and requires `chitty init`.

## Summary

Implemented stale-setup write gating. Non-autocommit repositories now require `chitty init`; autocommit repositories upgrade setup in a separate commit before the requested write; newer setup versions fail clearly. Updated `PLAN.md` and `README.md`; added regression coverage. Verification: `make check` (168 tests passed).

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
