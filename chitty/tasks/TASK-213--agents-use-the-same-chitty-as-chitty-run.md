---
title: Agents use the same `chitty` as `chitty run`
status: backlog
priority: high
created: 2026-11-06
---

## Description

Every Chitty write to a ticket should come from one Chitty version: the one running `chitty run`, from the main checkout. In this repository it doesn't. `agent_command` and `[agent_commands].claude` in `chitty.toml` wrap the agent in `uv run --no-sync`, which puts the ticket worktree's `.venv/bin` first on `PATH`, so the agent's bare `chitty` is the branch's code. The comment above `agent_command` says this is deliberate. The human decided on 2026-11-06 that it's a bug: the branch's code is unreviewed, it may be a different version, and it can write ticket state that `main`'s Chitty then can't read (`TASK-204`, `TASK-212`).

Changes:
1. Before starting the agent, `run` in `src/chitty/run.py` prepends the directory holding its own `chitty` executable to the agent's `PATH`. Take it from `shutil.which("chitty")` evaluated in the main checkout before anything changes `PATH`, and fail loudly if that is `None`. The agent's tests and `make` still use the worktree's own `.venv`, because `make` targets call it explicitly.
2. In this repository's `chitty.toml`, drop `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv run --no-sync` from `agent_command` and from `[agent_commands].claude`, and replace the comment with one saying the agent gets the runner's `chitty`.
3. Update the `chitty run` section of `README.md` and "Next action and runner" in `PLAN.md`.

Out of scope: running the agent in a container.

## Acceptance Criteria

- [ ] A test runs `chitty run` with a fake agent placed in the worktree's `.venv/bin` alongside a fake `chitty` there. The agent records which `chitty` its `PATH` resolves to, and the test asserts it is the runner's, not the worktree's. It fails before the fix.
- [ ] `chitty.toml` has no `uv run` in `agent_command` or `[agent_commands]`, and `README.md` and `PLAN.md` say the agent uses the runner's `chitty`.

## History

- 2026-11-06T16:24:16Z youthful-toad → backlog
