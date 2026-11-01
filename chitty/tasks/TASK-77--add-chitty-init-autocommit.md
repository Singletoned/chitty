---
title: Add `chitty init --autocommit`
status: review
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

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
