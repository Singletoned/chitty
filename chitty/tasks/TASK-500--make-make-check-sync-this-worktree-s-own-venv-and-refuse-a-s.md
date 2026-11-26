---
title: Make `make check` sync this worktree's own venv and refuse a symlinked one
status: doing
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

In the `check` target of `Makefile`:

1. As the first recipe line, refuse when `$(CURDIR)/.venv` is a symlink (`test -L`), with a message such as ``.venv is a symlink to another checkout's venv; run `rm .venv`, then `make install` ``. (`make install` alone would sync through the link too.) `UV_PROJECT_ENVIRONMENT` is already set by the Makefile, so the path is the only case.
2. Before the first `uv run` line, run `uv sync --all-extras --quiet`, so extras are current too.

Verify in scratch checkouts under a temporary directory, never against the main checkout's `.venv`: for the symlink case, link a scratch worktree's `.venv` to another scratch checkout's venv and compare that venv's file listing before and after; for the stale case, `uv pip uninstall mcp` in a scratch worktree's own venv.

Keep the `##` description, and check `mate --list` still lists the target.

### Out of scope

Node dependencies (`npm ci`); the `test` target; Chitty's runner setup.

## Acceptance Criteria

- [ ] With a scratch worktree whose `.venv` is a symlink to a scratch venv, `make check` exits non-zero before any `uv` command, printing the message naming `rm .venv` and `make install`; the linked venv's file listing is unchanged afterwards.
- [ ] In a scratch worktree with its own `.venv` after `uv pip uninstall mcp`, `make check` reinstalls `mcp` and pyright reports no `Import "mcp.server.mcpserver" could not be resolved`.
- [ ] `make check` passes in the ticket worktree, and `mate --list` still lists `check` with its description.

## History

- 2026-11-21T07:58:04Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:06Z nimble-umber-gannet: changed notes
- 2026-11-26T18:16:11Z calm-ochre-quail: replaced notes; changed title, labels, description, acceptance criteria
- 2026-11-26T18:16:11Z calm-ochre-quail backlog → cold-read
- 2026-11-26T18:18:58Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T18:18:58Z calm-ochre-quail cold-read → todo
- 2026-11-26T18:38:04Z mellow-silver-eel todo → doing
