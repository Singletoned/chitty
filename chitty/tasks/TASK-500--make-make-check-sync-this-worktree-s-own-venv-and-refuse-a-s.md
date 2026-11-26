---
title: Make `make check` sync this worktree's own venv and refuse a symlinked one
status: cold-read
labels:
  - bug
created: 2026-11-21
---

## Description

### Why

Two failures from the same gap: `make check` trusts whatever `.venv` it finds.

- 2026-11-20: an agent symlinked a hand-made worktree's `.venv` to the main checkout's to skip `make install`. `make check` there re-synced the shared venv, so the main checkout's editable `chitty` pointed at the worktree; once it was removed, `.venv/bin/chitty` in main failed with `bad interpreter` (and `chitty run --loop` uses it for every attempt).
- 2026-11-26, `.worktrees/task-10033`: an older `.venv` had a stale `mcp` package, so pyright reported `Import "mcp.server.mcpserver" could not be resolved` in `src/chitty/mcp.py`, unrelated to the change. `make install` fixed it. Each `uv run` in `check` syncs the project, but only its default dependencies; `mcp` is an extra (`make install` runs `uv sync --all-extras`), so it is never updated.

Decided (the person, 2026-11-26): `make check` refuses a symlinked `.venv` and otherwise syncs dependencies first.

### Change

In the `check` target of `Makefile`, before the other lines:

1. Refuse when `.venv` is a symlink, with a message such as ``.venv is a symlink; run `make install` in this worktree to give it its own venv``.
2. Run `uv sync --all-extras --quiet`, so extras are current too.

Keep the `##` description, and check `mate --list` still lists the target.

### Out of scope

Node dependencies (`npm ci`); the `test` target; Chitty's runner setup.

## Acceptance Criteria

- [ ] In a scratch linked worktree whose `.venv` is a symlink to another checkout's `.venv`, `make check` exits non-zero before running any `uv` command, with a message naming `.venv` and `make install`, and the other checkout's `.venv/bin/chitty` still runs afterwards. Without the change, `make check` there repoints the other venv.
- [ ] In a scratch worktree with its own `.venv` where `uv pip install mcp==<an older version the lock allows>` (or `uv pip uninstall mcp`) has made the `mcp` extra stale, `make check` re-syncs it and pyright no longer reports `Import "mcp.server.mcpserver" could not be resolved`. Without the change, the stale package stays and pyright fails. `make check` passes in this checkout.

## History

- 2026-11-21T07:58:04Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:06Z nimble-umber-gannet: changed notes
- 2026-11-26T18:16:11Z calm-ochre-quail: replaced notes; changed title, labels, description, acceptance criteria
- 2026-11-26T18:16:11Z calm-ochre-quail backlog → cold-read
