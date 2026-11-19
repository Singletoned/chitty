---
title: Move the setup upgrade commit into `init_repo` so a failed commit is restored
status: backlog
labels:
  - bug
priority: high
depends_on:
  - TASK-434
  - TASK-428
created: 2026-11-19
---

## Description

Second half of `TASK-434`, split out during planning on 2026-11-19. In an autocommit repository with an old `chitty_version`, `Repo._prepare_write` (`src/chitty/store.py`) calls `init_repo(self.root, False)` and then commits the files it returns as `chitty: upgrade repository setup`. If that commit fails (a refusing `pre-commit` hook, for example), the upgraded setup files stay modified and uncommitted: a probe on `main` on 2026-11-19 left ` M AGENTS.md` and ` M chitty.toml`. `Repo.refresh_setup` has the same shape.

Starts after `TASK-434` (which makes `init_repo` restore on any failure, including its own commit) and `TASK-428` (which puts a lock around `init_repo` and the setup commit in `_prepare_write`; keep that lock around the `init_repo` call). Plan the details when those have landed.

Direction agreed in planning: move the commit into `init_repo` so its restore covers it. `init_repo` gets a second required parameter `commit_message: str | None` (no default). `chitty init` passes `"chitty: initialize and enable autocommit"` with `--autocommit`, else `None`; `_prepare_write` passes `"chitty: upgrade repository setup"`; `refresh_setup` passes that message only when `git.is_repository(self.root)`, else `None`. Both delete their own `git.commit` calls. Only `enable_autocommit` requires a clean tree, as today.

## History

- 2026-11-19T21:17:37Z sunny-white-dormouse → backlog
- 2026-11-19T21:17:46Z sunny-white-dormouse: changed dependencies
