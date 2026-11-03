---
title: Stop `uv run` in a worktree repointing the shared `~/.envs/chitty` install
status: review
priority: high
created: 2026-11-03
---

## Description

On 2026-11-03 `chitty` in the main checkout failed with `ModuleNotFoundError: No module named 'chitty'` because the editable install in `~/.envs/chitty` pointed at the removed `.worktrees/task-107/src`. `TASK-103` made `make` targets use a worktree-local `.venv`, but `.envrc` still exports `UV_PROJECT_ENVIRONMENT=~/.envs/chitty` to every worktree, so any `uv` command outside `make` re-syncs the shared environment. The TASK-107 worker ran `uv run --project ../task-107 chitty edit ...` at 10:46:53, the only such command found in that window (the entry script mtime was 10:43, not fully explained). Also, `make install` in main now targets `.venv`, so nothing keeps `~/.envs/chitty`, the `chitty` first on `PATH`, up to date. Likely fix: stop exporting the shared environment, so that PATH and `uv` use each checkout's `.venv`.

## Acceptance Criteria

- [x] `README.md` and `PLAN.md` describe the editable global `chitty` and per-checkout `.venv` files
- [x] `uv` commands in a worktree no longer repoint another environment
- [x] The global `chitty` runs the main checkout in this and other repositories

## Plan

Reverse `TASK-81`: document that this machine's global `chitty` is an editable install of the main checkout and why, in `README.md` and `PLAN.md`. Record the local `.envrc` change and the suggestion sent to `prj`. Deleting `~/.envs/chitty` is left for the human once running sessions have restarted.

## Notes

Decision (human, 2026-11-03): remove the shared environment rather than guard against it. Done locally: `.envrc` (untracked) now only does `PATH_add .venv/bin` and exports neither `VIRTUAL_ENV` nor `UV_PROJECT_ENVIRONMENT`. Verified that `uv run --project <worktree>` with those unset uses the worktree `.venv` and leaves the main `.venv` untouched. Still to do: stop `prj` generating the shared-environment `.envrc`, because `prj update` would restore it; delete `~/.envs/chitty` once running sessions no longer inherit it.

Verified: `uv run --project <worktree>` with the variables unset used that worktree `.venv` and left the main `.venv` unchanged; `make install` and `make check` in this worktree left `~/.envs/chitty` and the main `.venv` on the main checkout; `~/.local/bin/chitty` reports 0.1.19, runs from the main checkout `src`, and listed tasks here and in `circuitry`. `.envrc` is untracked, so the reviewer can only check it on this machine. Not verified through direnv, because the edited `.envrc` needs `direnv allow` from the human. Left for the human: delete `~/.envs/chitty` once running `pi` sessions have restarted. The `prj` fix was sent as a suggestion. Follow-ups: `TASK-119`, `TASK-120`, `TASK-121`, `TASK-122`.

## Summary

Global `chitty` is now an editable install of the main checkout; each checkout uses its own `.venv` through `make` and `uv run`, and `.envrc` sets no environment variables or `PATH`. `README.md` and `PLAN.md` record this and reverse `TASK-81`. Verification: `make check` (197 tests) plus the checks in Notes. Follow-ups: `TASK-119` to `TASK-122`, the `prj` suggestion, and deleting `~/.envs/chitty`.

## History

- 2026-11-03T11:27:22Z eager-raven → todo
- 2026-11-03T11:28:11Z eager-raven: changed notes
- 2026-11-03T11:39:05Z eager-raven: wrote the plan
- 2026-11-03T11:39:05Z eager-raven todo → doing
- 2026-11-03T11:40:32Z eager-raven: changed acceptance criteria
- 2026-11-03T11:40:33Z eager-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-03T11:40:33Z eager-raven doing → review
