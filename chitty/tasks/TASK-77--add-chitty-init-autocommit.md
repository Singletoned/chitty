---
title: Add `chitty init --autocommit`
status: done
priority: high
created: 2026-11-01
---

## Description

Turning on autocommit today means running `chitty init`, editing `chitty.toml` by hand, and committing what `init` wrote. `chitty init --autocommit` should set `autocommit = true` in the config and commit the files `init` itself wrote or changed (config, `AGENTS.md` guide block, `CLAUDE.md` symlink), and nothing else. Like other autocommits, it should fail loudly if Git cannot commit, rather than leaving the work half done. Decide whether it refuses to run, or simply leaves other changes alone, when the working tree already has unrelated changes.

## Acceptance Criteria

- [x] `chitty init --autocommit` sets `autocommit = true` in the repository config
- [x] It commits only the paths `init` wrote or changed, with a message that says so; other changes in the working tree are left unstaged and uncommitted
- [x] Re-running it when nothing needs changing writes and commits nothing
- [x] `README.md`, `PLAN.md` and `init --help` describe it

## Plan

Add an explicit `--autocommit` option to `init`. Refuse it on a dirty Git working tree, so the setup commit is unambiguous. Track only repository-local files changed by init, create/refresh the `CLAUDE.md` symlink, and use the existing path-limited Git commit helper. Cover success, no-op, dirty paths, and commit failure; then update the CLI help and documentation.

## Notes

Implemented with a clean-tree precondition agreed during this session. Verified with `make check`, `chitty fix`, and `chitty init --help`.

Review found that a failed setup commit left generated files behind, and that commented `autocommit = false` lines were not enabled. Fixing both before re-review.

Addressed review findings: setup files roll back when the commit fails, and commented `autocommit = false` settings are enabled.

Reviewed: confirmed independent implementation by Ed Singleton in commits 234eae2 and 2c5ab43; inspected the clean-tree guard, path-limited setup commit, idempotence, rollback, tests, and documentation. Verified independently with make check (163 tests).

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
