---
title: Put only the runner's `chitty` on a worker's `PATH`, not its whole `.venv/bin`
status: planning
labels:
  - bug
priority: high
created: 2026-11-25
moved_from: TASK-SSVZJ6
---

## Description

`chitty run` puts the runner's whole `.venv/bin` first on the agent's `PATH`, so agents call the runner's `chitty` (often ahead of the released one). It does this twice in `src/chitty/run.py`: in review preparation (around line 577) and before work sessions (around line 627). That install is editable and points at the runner checkout's `src/`, so a worker in `.worktrees/task-<n>` that runs a bare `pytest` or `python` imports that checkout's code, not its worktree's. `make check` is not affected, because it uses the worktree's own `.venv`.

Seen 2026-11-25 in a worker trial: a worker ran bare `pytest` against a placeholder as its ticket asked, got the runner checkout's code, where the feature had already landed, saw the properties pass, and wrongly sent the ticket back to `planning`. With the worktree's code they fail.

Change: one helper in `run.py`, used at both places, that makes a directory holding only a `chitty` symbolic link to the runner's `chitty`, under the Git common directory (beside the run locks, `.git/chitty/run/`; for example `.git/chitty/bin/`), replacing an existing link, and puts that directory first on the agent's `PATH` instead of `.venv/bin`. Keep today's `runner chitty executable not found` error.

A fake agent as in `tests/test_run_repair_mode.py` (`agent_command = "fake-agent {mode} {id} {prompt}"`) can record what it resolves. No property test: a fixed environment change, shown by one example per agent mode.

Out of scope: work guide advice about bare `pytest` (the trap goes away instead).

## Acceptance Criteria

- [ ] A runner test with a fake work agent that records `command -v chitty`, `command -v pytest` and `command -v python` from its own environment: `chitty` resolves to a link to the runner's `chitty` (`Path(sys.executable).parent / "chitty"`), and `pytest` and `python` do not resolve into the runner's `.venv/bin`. The same for a review agent. Fails today: both resolve into the runner's `.venv/bin`.
- [ ] Regression tests: the existing `chitty run` tests pass, including `runner chitty executable not found` handling; `make check` passes.

## History

- 2026-11-25T22:28:25Z calm-ochre-quail → backlog
- 2026-11-25T22:28:27Z calm-ochre-quail: changed notes
- 2026-11-25T22:34:11Z calm-ochre-quail: changed title, labels, priority
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-SSVZJ6
- 2026-11-25T23:48:15Z calm-ochre-quail: replaced notes; changed description, acceptance criteria
- 2026-11-25T23:48:15Z calm-ochre-quail backlog → planning
- 2026-11-25T23:48:29Z calm-ochre-quail planning → cold-read
- 2026-11-25T23:49:43Z calm-ochre-quail: changed description
- 2026-11-25T23:49:43Z calm-ochre-quail cold-read → planning
