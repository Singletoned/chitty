---
title: Put only the runner's `chitty` on a worker's `PATH`, not its whole `.venv/bin`
status: backlog
labels:
  - bug
priority: high
created: 2026-11-25
provisional: true
---

## Description

Found in the worker trials on 2026-11-25. `chitty run` puts the runner's own `.venv/bin` (the main checkout's) first on the agent's `PATH` (`src/chitty/run.py` around lines 580 and 631). That install is editable and points at the main checkout's `src/`. So when a worker in `.worktrees/task-N` runs a bare `pytest` or `python`, it imports `main`'s code, not the worktree's. `make check` is not affected, because the Makefile sets `UV_PROJECT_ENVIRONMENT` to the worktree's own `.venv`.

What happened in a trial: luna (Pi 1.5.2) ran bare `pytest` against a `NotImplementedError` placeholder, as `TASK-512` asked. pytest resolved to another checkout's `.venv`, whose code already held the landed feature, so the five properties passed. Luna then returned the ticket to `planning`, claiming the properties don't fail without the change. Run with the worktree's code, they fail (9 errors).

Options: put only the runner's `chitty` executable on `PATH` (for example a directory holding just a `chitty` link) rather than the whole `.venv/bin`; or tell workers in the work guide to run tests through the project's own commands. The first removes the trap without relying on the agent.

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:25Z calm-ochre-quail → backlog
- 2026-11-25T22:28:27Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:11Z calm-ochre-quail: changed title, labels, priority
