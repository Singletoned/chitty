---
title: Clear `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` for setup and check commands
status: todo
priority: low
created: 2026-11-10
---

## Description

`chitty run` removes `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` from the agent's environment (`src/chitty/run.py:233`), but `_setup`, `_run_check` and `_landing_check` in the same file pass the launching shell's environment through. With those variables pointing at a shared environment, `uv sync` in a ticket worktree installs into the shared one, and worktree `.venv/bin/...` paths fail. Reported from mullion and Shelfpath.

Decision: one helper in `run.py` returns a copy of `os.environ` without those two variables; the agent launch and all three commands use it via `env=`. Do not unset anything else.

Implement this now. The person is also fixing their shell environment globally, so a follow-up human ticket reviews on or after 2026-11-17 whether this code is still needed, and removes it if not.

## Acceptance Criteria

- [ ] With both variables set in `os.environ`, tests running `_setup`, `_run_check` and `_landing_check` with a command that writes its environment to a file show neither variable; each test fails before the fix.

## Notes

Cold read 1 (Haiku): no serious findings. Accepted: the agent launch is already covered by `test_run_uses_runner_chitty_and_strips_worktree_environment` in `tests/test_next.py`; keep it as the launch check, no new launch test needed. A `_run_check` test may build a real repo with one ticket (`Repo.open`, `NextAction`). Possible starting point: `git diff main...refs/cold-read/TASK-238/1`; check it against the current criteria, not trust it.

## History

- 2026-11-10T14:08:39Z jolly-heron → backlog
- 2026-11-10T14:15:02Z jolly-heron: changed notes
- 2026-11-10T14:15:33Z jolly-heron: changed description
- 2026-11-10T14:16:08Z jolly-heron backlog → todo
