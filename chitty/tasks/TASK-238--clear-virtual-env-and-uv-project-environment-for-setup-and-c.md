---
title: Clear `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` for setup and check commands
status: done
priority: low
created: 2026-11-10
---

## Description

`chitty run` removes `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` from the agent's environment (`src/chitty/run.py:233`), but `_setup`, `_run_check` and `_landing_check` in the same file pass the launching shell's environment through. With those variables pointing at a shared environment, `uv sync` in a ticket worktree installs into the shared one, and worktree `.venv/bin/...` paths fail. Reported from mullion and Shelfpath.

Decision: one helper in `run.py` returns a copy of `os.environ` without those two variables; the agent launch and all three commands use it via `env=`. Do not unset anything else.

Implement this now. The person is also fixing their shell environment globally, so a follow-up human ticket reviews on or after 2026-11-17 whether this code is still needed, and removes it if not.

## Acceptance Criteria

- [x] With both variables set in `os.environ`, tests running `_setup`, `_run_check` and `_landing_check` with a command that writes its environment to a file show neither variable; each test fails before the fix.

## Plan

Replace the mocked _run_check assertion with a real child process that records its environment, matching the setup and landing-check tests. Run the focused test with the environment helper temporarily disabled to prove it fails, restore the fix, then run formatting and checks.

## Notes

Cold read 1 (Haiku): no serious findings. Accepted: the agent launch is already covered by `test_run_uses_runner_chitty_and_strips_worktree_environment` in `tests/test_next.py`; keep it as the launch check, no new launch test needed. A `_run_check` test may build a real repo with one ticket (`Repo.open`, `NextAction`). Possible starting point: `git diff main...refs/cold-read/TASK-238/1`; check it against the current criteria, not trust it.

Regression tests failed before implementation for setup and landing-check; all three command paths now pass with both variables set. make format and make check pass (426 Python tests and Node tests). Test for _run_check verifies subprocess env directly; setup and landing check execute a child that records its environment.

Review failed (tests): `uv run python -m unittest tests.test_run_environment -v` printed 3 tests OK, and `make format && make check` passed 439 Python tests and the Node tests.

1: fail - The `_run_check` test mocks `subprocess.run` and runs `true` instead of running a command that writes its environment to a file. Replace the mock with a real child command that records its environment, and demonstrate that this test fails against the unfixed behavior and passes with the fix.

Replaced the _run_check subprocess mock with a real child that records its environment. Confirmed this regression test fails when _command_environment stops stripping the variables, then passes with the fix. make format && make check passed.

Reviewed: `make format && make check` passed (451 Python tests and Node tests). HUMAN-10 tracks the follow-up.

1: pass - All three real child-process environment tests pass; substituting an unfiltered environment makes all three fail.

## Summary

Updated the _run_check regression test to verify a real child process environment. Confirmed failure with environment stripping disabled; make format && make check passed. Implementation remains committed as c2c7d57; test update committed separately. Follow-up: review necessity on or after 2026-11-17.

## History

- 2026-11-10T14:08:39Z jolly-heron → backlog
- 2026-11-10T14:15:02Z jolly-heron: changed notes
- 2026-11-10T14:15:33Z jolly-heron: changed description
- 2026-11-10T14:16:08Z jolly-heron backlog → todo
- 2026-11-10T17:21:14Z witty-zander todo → doing
- 2026-11-10T17:21:29Z witty-zander: wrote the plan
- 2026-11-10T17:23:56Z witty-zander: changed notes, summary; ticked acceptance criteria
- 2026-11-10T17:23:57Z witty-zander doing → review
- 2026-11-10T18:18:14Z eager-puffin: changed acceptance criteria, notes
- 2026-11-10T18:18:14Z eager-puffin review → doing
- 2026-11-10T22:21:29Z calm-dormouse: wrote the plan
- 2026-11-10T22:23:13Z calm-dormouse: changed notes
- 2026-11-10T22:23:30Z calm-dormouse: changed summary; ticked acceptance criteria
- 2026-11-10T22:23:30Z calm-dormouse doing → review
- 2026-11-10T22:27:18Z friendly-otter: changed notes; ticked acceptance criteria
- 2026-11-10T22:27:18Z friendly-otter review → done
