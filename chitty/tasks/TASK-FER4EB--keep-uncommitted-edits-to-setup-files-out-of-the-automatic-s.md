---
title: Keep uncommitted edits to setup files out of the automatic setup upgrade commit
status: backlog
labels:
  - bug
depends_on:
  - TASK-464
created: 2026-11-24
provisional: true
---

## Description

Split from `TASK-133` (2026-11-24). In an autocommit repository with a stale `chitty_version`, the first write (`Repo._prepare_write` in `src/chitty/store.py`) runs `init_repo` and commits the setup files it changed as `chitty: upgrade repository setup`. `git.commit` commits whole files, so an uncommitted edit someone had made to one of them goes into that commit too.

Probed on `main` at `80f6f701`: after `chitty init` and a commit, set `chitty_version = "0.0.0"`, remove the managed block from `AGENTS.md` and commit; then add an uncommitted line `MY UNCOMMITTED NOTE` at the top of `AGENTS.md` and run `chitty add T -d x`. The `chitty: upgrade repository setup` commit changes `AGENTS.md` and contains the line, and `git status --porcelain` is empty afterwards.

`Repo.refresh_setup` already refuses in this case (`repository setup files have uncommitted changes; commit or stash these first`); `_prepare_write` does not. To decide while planning: refuse in the same way, or skip the upgrade for that write with a warning. Plan after `TASK-464` lands, since it moves that commit into `init_repo`.

## History

- 2026-11-24T08:42:39Z kind-navy-toad → backlog
- 2026-11-24T08:43:22Z kind-navy-toad: changed dependencies, description
