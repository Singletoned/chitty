---
title: Time out the runner `setup` and `check` commands
status: planning
labels:
  - needs-minor
priority: high
depends_on:
  - TASK-426
  - TASK-430
created: 2026-11-19
---

## Description

On 2026-11-19 the `chitty run --mode review` check for `TASK-428` ran `make check` for over 27 minutes and would never have finished (one test worker deadlocked on a lock). The runner runs `setup`, `check` and the landing check with no timeout, so a hung command stalls the loop with no error and no ticket note. Agent sessions already have `agent_timeout` (`DEFAULT_AGENT_TIMEOUT = 7200` in `src/chitty/config.py`, killed by `_run_agent` in `src/chitty/run.py`).

Starts after `TASK-426` and `TASK-430`, which change the same functions. After `TASK-426`, `_setup`, `_run_check` and `_landing_check` in `src/chitty/run.py` all run their command through `_run_logged(phase: str, command: str, worktree: Path) -> int` (added by `TASK-353`), which writes `# chitty <phase>: <command>`, the output and `# exit <code>` to `.chitty/check.log` in the worktree. They are not on `main` yet; the dependencies hold this ticket until they are. If, once they have landed, those functions differ from this description, return the ticket to `planning`.

Decisions:

- New repository setting `command_timeout`: a non-negative integer number of seconds, `0` for no limit, default `DEFAULT_COMMAND_TIMEOUT = 3600` (a module constant in `src/chitty/config.py`, next to `DEFAULT_AGENT_TIMEOUT`), declared like `agent_timeout` on the config model. One setting covers all three phases.
- `_run_logged` gains a required `timeout: int` parameter (no default value); every caller passes `repo.config.command_timeout` from the repository it already uses for that phase. It starts the command with `subprocess.Popen` (same `cwd`, `stdin`, `env` and log redirection as now) and waits with `timeout or None`.
- On expiry it stops the command and its descendants exactly as `_run_agent` stops an agent: `SIGTERM` to the process and its descendants, `SIGKILL` to any left after `AGENT_KILL_GRACE_SECONDS`. Move that logic out of `_run_agent` into one helper both call, so there is one copy. Never use `start_new_session` (see `docs/plan/next-action-and-runner.md`).
- After stopping it, `_run_logged` ends the log with a newline if needed and `# timed out after <N> seconds`, then raises `CommandTimedOut`, a new `ChittyError` subclass in `src/chitty/run.py`, whose message is exactly `` <phase> timed out after <N> seconds; output in `.chitty/check.log` ``.
- `_setup` and `_landing_check` let it propagate, so it is recorded as their existing failures are (`Runner error (setup)` and so on). `_run_check` catches it and passes its message to `_handle_check_failure` as `detail` with `exited=True`, so it is handled exactly like a check that exited non-zero.
- Document `command_timeout` next to `agent_timeout` in `README.md`, `docs/plan/config.md` (the commented example block) and `docs/plan/next-action-and-runner.md`.
- Label `needs-minor`: a `setup` or `check` that runs longer than an hour now fails.

Tests. The setting is a validator, so it gets a Hypothesis property (the repository tool). The rest has no property: it is stopping real processes, and its only pure part, the message, is fixed text. Each hanging command prints a marker, starts a child that sleeps 30 seconds, then sleeps 30 seconds itself, and every test sets a timeout of 1 second and asserts the call returns in under 15 seconds. That bound is what makes the tests fail, rather than hang, on the code before the change. Follow `tests/test_run_timeout.py` (`TestDirectAgentTimeout` for the direct call, `TestAgentTimeout` for a `chitty run` with a fake command on `PATH`), checking each recorded PID with `ps` as it does.

## Acceptance Criteria

- [ ] Property in `tests/test_config.py`, modelled on `test_agent_timeout_requires_nonnegative_toml_integer`: for any integer from `st.integers()`, a config with `command_timeout = <n>` loads with that value when `n >= 0` and is a config error naming `command_timeout` when `n < 0`; with the key absent it is `3600`. `grep -n command_timeout README.md docs/plan/config.md docs/plan/next-action-and-runner.md` finds it in each, next to `agent_timeout`.
- [ ] A direct test in a new `tests/test_command_timeout.py` calls `_run_logged("check", <hanging command>, worktree, 1)`: it raises `CommandTimedOut` with the exact message, returns in under 15 seconds, the command and its child are gone, and the log starts with `# chitty check: `, contains the marker and ends with `# timed out after 1 seconds\n`. With timeout `0`, a command that sleeps 2 seconds, prints and exits 3 returns `3` after at least 2 seconds and the log ends `# exit 3\n`.
- [ ] In the same file, `chitty run` on a `todo` ticket with `command_timeout = 1` and a hanging `check` finishes in under 15 seconds, prints `TASK-1: todo → error`, and the branch ticket note contains `` check timed out after 1 seconds; output in `.chitty/check.log` ``; with a hanging `setup` instead, the note contains `Runner error (setup)` and `` setup timed out after 1 seconds ``.
- [ ] A landing whose landing check hangs, with `command_timeout = 1`, finishes in under 15 seconds, leaves `main` unchanged, and records `` landing check timed out after 1 seconds `` the way `tests/test_review_merge.py` checks a failing landing check today.
- [ ] Against the `run.py` of `main` just before this change (with `TASK-426` landed), with only the new `timeout` argument added to `_run_logged` and ignored, each new test in criteria 2 to 4 fails on a timing or message assertion, not with `TypeError` or `AttributeError` (record the failing assertion of each in a note); `make check` passes.

## Notes

Suggestion origin: chitty

Planner, 2026-11-19: written against `_run_logged` from `TASK-353` and `TASK-426`, which have not landed (`TASK-353` is still in planning). Keep this ticket in `planning`; once `TASK-426` is `done`, check the description against `src/chitty/run.py`, cold-read again, then move it to `todo`.

## History

- 2026-11-19T20:55:24Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:25Z sunny-white-dormouse: changed notes
- 2026-11-19T21:03:18Z sunny-white-dormouse: changed labels, priority, dependencies, description, acceptance criteria
- 2026-11-19T21:03:18Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:04:02Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:04:59Z sunny-white-dormouse: changed description, acceptance criteria, notes
- 2026-11-19T21:04:59Z sunny-white-dormouse cold-read → planning
