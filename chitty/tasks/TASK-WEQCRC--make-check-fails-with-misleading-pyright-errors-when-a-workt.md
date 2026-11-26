---
title: make check fails with misleading pyright errors when a worktree .venv is stale
status: backlog
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

Seen 2026-11-26 in `.worktrees/task-10033`: a `.venv` created earlier had an older `mcp` package, so `make check` failed with pyright `Import "mcp.server.mcpserver" could not be resolved` in `src/chitty/mcp.py`, unrelated to the change being checked. `make install` fixed it. Suggest `make check` (or the worktree setup) re-sync dependencies, e.g. run `uv sync` first when `uv.lock` is newer than `.venv`, so workers do not chase phantom failures.

## Notes

Suggestion origin: chitty

Related: TASK-500 (a worktree whose `.venv` is a symlink to the main checkout's). Syncing dependencies in `make check` must not repoint a shared venv, so the two fixes should be decided together.

Merged into TASK-500, which now covers both the stale extra and the symlinked venv.

## History

- 2026-11-26T18:06:07Z calm-ochre-quail → backlog
- 2026-11-26T18:06:09Z calm-ochre-quail: changed notes
- 2026-11-26T18:07:25Z calm-ochre-quail: changed labels, notes
- 2026-11-26T18:16:33Z calm-ochre-quail: changed notes
