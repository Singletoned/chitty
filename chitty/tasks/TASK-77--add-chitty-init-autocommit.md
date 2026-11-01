---
title: Add `chitty init --autocommit`
status: backlog
created: 2026-11-01
---

## Description

Turning on autocommit today means running `chitty init`, editing `chitty.toml` by hand, and committing what `init` wrote. `chitty init --autocommit` should set `autocommit = true` in the config and commit the files `init` itself wrote or changed (config, `AGENTS.md` guide block, `CLAUDE.md` symlink), and nothing else. Like other autocommits, it should fail loudly if Git cannot commit, rather than leaving the work half done. Decide whether it refuses to run, or simply leaves other changes alone, when the working tree already has unrelated changes.

## Acceptance Criteria

- [ ] `chitty init --autocommit` sets `autocommit = true` in the repository config
- [ ] It commits only the paths `init` wrote or changed, with a message that says so; other changes in the working tree are left unstaged and uncommitted
- [ ] Re-running it when nothing needs changing writes and commits nothing
- [ ] `README.md`, `PLAN.md` and `init --help` describe it

## History

- 2026-11-01 → backlog
