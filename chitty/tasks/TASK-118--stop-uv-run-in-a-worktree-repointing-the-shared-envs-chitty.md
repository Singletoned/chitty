---
title: Stop `uv run` in a worktree repointing the shared `~/.envs/chitty` install
status: todo
priority: high
created: 2026-11-03
---

## Description

On 2026-11-03 `chitty` in the main checkout failed with `ModuleNotFoundError: No module named 'chitty'` because the editable install in `~/.envs/chitty` pointed at the removed `.worktrees/task-107/src`. `TASK-103` made `make` targets use a worktree-local `.venv`, but `.envrc` still exports `UV_PROJECT_ENVIRONMENT=~/.envs/chitty` to every worktree, so any `uv` command outside `make` re-syncs the shared environment. The TASK-107 worker ran `uv run --project ../task-107 chitty edit ...` at 10:46:53, the only such command found in that window (the entry script mtime was 10:43, not fully explained). Also, `make install` in main now targets `.venv`, so nothing keeps `~/.envs/chitty`, the `chitty` first on `PATH`, up to date. Likely fix: stop exporting the shared environment, so that PATH and `uv` use each checkout's `.venv`.

## Notes

Decision (human, 2026-11-03): remove the shared environment rather than guard against it. Done locally: `.envrc` (untracked) now only does `PATH_add .venv/bin` and exports neither `VIRTUAL_ENV` nor `UV_PROJECT_ENVIRONMENT`. Verified that `uv run --project <worktree>` with those unset uses the worktree `.venv` and leaves the main `.venv` untouched. Still to do: stop `prj` generating the shared-environment `.envrc`, because `prj update` would restore it; delete `~/.envs/chitty` once running sessions no longer inherit it.

## History

- 2026-11-03T11:27:22Z eager-raven → todo
- 2026-11-03T11:28:11Z eager-raven: changed notes
