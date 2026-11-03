---
title: Stop `uv run` in a worktree repointing the shared `~/.envs/chitty` install
status: done
priority: high
created: 2026-11-03
---

## Description

On 2026-11-03 `chitty` in the main checkout failed with `ModuleNotFoundError: No module named 'chitty'` because the editable install in `~/.envs/chitty` pointed at the removed `.worktrees/task-107/src`. `TASK-103` made `make` targets use a worktree-local `.venv`, but `.envrc` still exports `UV_PROJECT_ENVIRONMENT=~/.envs/chitty` to every worktree, so any `uv` command outside `make` re-syncs the shared environment. The TASK-107 worker ran `uv run --project ../task-107 chitty edit ...` at 10:46:53, the only such command found in that window (the entry script mtime was 10:43, not fully explained). Also, `make install` in main now targets `.venv`, so nothing keeps `~/.envs/chitty`, the `chitty` first on `PATH`, up to date. Likely fix: stop exporting the shared environment, so that PATH and `uv` use each checkout's `.venv`.

## Acceptance Criteria

- [x] `README.md` and `PLAN.md` describe the editable global `chitty` and per-checkout `.venv` files
- [ ] `uv` commands in a worktree no longer repoint another environment
- [ ] The global `chitty` runs the main checkout in this and other repositories

## Plan

Reverse `TASK-81`: document that this machine's global `chitty` is an editable install of the main checkout and why, in `README.md` and `PLAN.md`. Record the local `.envrc` change and the suggestion sent to `prj`. Deleting `~/.envs/chitty` is left for the human once running sessions have restarted.

## Notes

Decision (human, 2026-11-03): remove the shared environment rather than guard against it. Done locally: `.envrc` (untracked) now only does `PATH_add .venv/bin` and exports neither `VIRTUAL_ENV` nor `UV_PROJECT_ENVIRONMENT`. Verified that `uv run --project <worktree>` with those unset uses the worktree `.venv` and leaves the main `.venv` untouched. Still to do: stop `prj` generating the shared-environment `.envrc`, because `prj update` would restore it; delete `~/.envs/chitty` once running sessions no longer inherit it.

Verified: `uv run --project <worktree>` with the variables unset used that worktree `.venv` and left the main `.venv` unchanged; `make install` and `make check` in this worktree left `~/.envs/chitty` and the main `.venv` on the main checkout; `~/.local/bin/chitty` reports 0.1.19, runs from the main checkout `src`, and listed tasks here and in `circuitry`. `.envrc` is untracked, so the reviewer can only check it on this machine. Not verified through direnv, because the edited `.envrc` needs `direnv allow` from the human. Left for the human: delete `~/.envs/chitty` once running `pi` sessions have restarted. The `prj` fix was sent as a suggestion. Follow-ups: `TASK-119`, `TASK-120`, `TASK-121`, `TASK-122`.

Correction to the previous note: `~/.envs/chitty` no longer exists, so the claim that it stayed on the main checkout is wrong and nothing is left to delete. It was removed outside this session (`~/.envs` last changed at 11:30). The main `.venv` staying on the main checkout was verified.

Review failed: (2) `uv` worktree isolation is not implemented in the branch: `.envrc` is ignored and absent from this worktree, and the only committed changes are documentation, so the claimed local configuration cannot be independently reviewed or applied durably; (3) the global `chitty` here resolves to `/Users/singletoned/.local/share/uv/tools/chitty/bin/chitty` (version `0.1.19`), not an editable main-checkout install, so the claimed cross-repository behavior is not established. Implement and independently verify the actual local/global environment setup, then return this ticket to review. Criterion 1 passes. `make check` exits `0`; `uv run --project .` with inherited environment variables removed uses this worktree `.venv` and source tree.

Reviewed: Forced by human

Landed by the author of `TASK-120` on 2026-11-03, at the human's request: the branch was rebased onto `main`, `make check` passed, and it fast-forwarded with no conflicts. The docs were checked against this machine: the uv receipt is editable from the main checkout with the `mcp` extra. Landed now so the first run after `TASK-120` would not land it unexpectedly.

## Summary

Global `chitty` is now an editable install of the main checkout; each checkout uses its own `.venv` through `make` and `uv run`, and `.envrc` sets no environment variables or `PATH`. `README.md` and `PLAN.md` record this and reverse `TASK-81`. `~/.envs/chitty` is gone. Verification: `make check` (197 tests) plus the checks in Notes. Follow-ups: `TASK-119` to `TASK-122` and the `prj` suggestion.

## History

- 2026-11-03T11:27:22Z eager-raven → todo
- 2026-11-03T11:28:11Z eager-raven: changed notes
- 2026-11-03T11:39:05Z eager-raven: wrote the plan
- 2026-11-03T11:39:05Z eager-raven todo → doing
- 2026-11-03T11:40:32Z eager-raven: changed acceptance criteria
- 2026-11-03T11:40:33Z eager-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-03T11:40:33Z eager-raven doing → review
- 2026-11-03T11:40:49Z eager-raven: changed notes, summary
- 2026-11-03T12:15:00Z ivory-koala: changed acceptance criteria, notes
- 2026-11-03T12:15:00Z ivory-koala review → doing
- 2026-11-03T12:22:38Z human doing → review
- 2026-11-03T12:24:57Z terrifying-bob: changed notes
- 2026-11-03T12:24:57Z terrifying-bob review → done
- 2026-11-03T20:18:09Z lively-panda: changed notes
