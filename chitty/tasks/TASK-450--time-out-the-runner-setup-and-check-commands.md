---
title: Time out the runner `setup` and `check` commands
status: done
labels:
  - needs-minor
priority: high
depends_on:
  - TASK-426
  - TASK-430
created: 2026-11-19
---

## Description

A hung runner check stopped a review on 2026-11-19. Apply one per-invocation deadline to every runner `setup`, pre-agent `check`, and landing validation command (whether `landing_check` is configured or falls back to `check`). This includes review setup, landing setup and pending landing retries. No timeout for the run as a whole. `TASK-426` and `TASK-430` have landed; all three command paths now use `_run_logged` in `src/chitty/run.py`.

Add `command_timeout` in `src/chitty/config.py` as a strict nonnegative integer in seconds, default `DEFAULT_COMMAND_TIMEOUT = 3600`, with zero meaning no timeout. Follow `agent_timeout` for the field definition. Document it next to `agent_timeout` in `README.md`, `docs/plan/config.md`, and `docs/plan/next-action-and-runner.md`, including the per-command scope and the existing failure routing. Keep `needs-minor`: a command that runs longer than an hour now fails unless configured otherwise. Do not edit the repository config.

Pass a required `timeout` to `_run_logged(phase, command, worktree, timeout)` through `_setup`, `_run_check` and `_landing_check`. Use the main repository config at both `_run_ticket` and `_land_locked` call sites. Replace `subprocess.run` in `_run_logged` with `Popen` and `wait(timeout=timeout or None)`. Keep argv splitting, cwd, environment, closed stdin, binary merged output and log replacement. Preserve interrupt behavior: use a `Popen` context manager and on an exception leaving the wait block kill the direct child (as `subprocess.run` does) before re-raising; do not convert an interrupt to a timeout. Leave normal and missing-command behavior unchanged.

Extract the timeout cleanup in `_run_agent` into one helper used by both paths. Preserve its process-table snapshot, `SIGTERM`, grace period, `SIGKILL` of survivors and final wait without changing the process group. Processes outside the captured descendant tree (for example a detached Docker container) are out of scope. After cleanup append `# timed out after <N> seconds` and a newline to `.chitty/check.log`, using the existing binary newline handling. Do not append an exit footer on timeout. Raise `CommandTimedOut`, a `ChittyError` subclass in `run.py`, with exact text `<phase> timed out after <N> seconds; output in ` plus the log path in backticks. Phase names are `setup`, `check` and `landing check`.

Let setup and landing propagate the error to their existing callers. `_run_check` handles the timeout via `_handle_check_failure` with `exited=True` and the timeout message as detail; it follows the same status-dependent routing as a nonzero exit. Do not change that routing, pending-landing policy, agent timeouts or the runner loop.

Use real Python children and temporary Git fixtures. For the direct test, run a script that writes a flushed marker without a trailing newline, records its PID and a sleeping child's PID outside the log, waits for the child, then exits 7. Each script has a finite fallback (about 5 seconds) so unfixed tests cannot hang. On timeout assert the exact exception and binary footer, marker preservation and absent/zombie states for both recorded PIDs as in `tests/test_run_timeout.py`. For the `doing` case use a fake agent that writes a start marker outside the worktree and makes a normal committed status handoff as in `tests/test_next.py`; check the note survives and the marker is present. For the landing case set `landing_check` and `command_timeout` in the fixture before branching to avoid a config change on the ticket branch; adapt `test_landing_failure_records_error_on_branch_without_advancing_main` and use an executable slow script that returns zero if not timed out. No property for real-process routing or cleanup: those depend on actual process and Git state; the config validation has the property above.

Regression evidence: run the new timeout cases once with the deadline ignored in `_run_logged` (use `wait()` there, leave wiring intact) and record the failed behavioral assertions, then restore the deadline and run `make check`. Use this one temporary mutation rather than committing integration mutants that repeatedly spawn Git, process trees and agent fixtures for behavior already covered by the real-process tests.

## Acceptance Criteria

- [ ] In `tests/test_config.py`, generate signed 64-bit integers with Hypothesis: a TOML `command_timeout` loads unchanged when nonnegative and is rejected with an error naming the key otherwise. Also cover the omitted default and rejection of TOML `true`, `1.0` and `"1"`.
- [ ] In `tests/test_command_timeout.py`, direct real-process tests show that `_run_logged` times out, raises the exact error, terminates the command and its child, and produces the specified timeout log. With timeout zero, the same finite command instead exits 7 and logs `# exit 7`.
- [ ] Run `chitty run --mode work` through `CliTestCase` on a fresh `todo` ticket with a real slow setup or check and `command_timeout = 1`. Each case returns `TASK-1: todo → error`, with the matching phase in the branch ticket note and the timeout footer in the worktree log; a fake agent must not run. Also exercise the existing continue-on-check-failure path for a `doing` ticket: a fake agent runs and the ticket records `Check failed before this session: check timed out`.
- [ ] In `tests/test_review_merge.py`, use a passing fake reviewer and a dedicated slow `landing_check`, with normal setup and check. `chitty run --mode review` reports `done → error`, leaves the pre-run `main` HEAD unchanged, and retains the branch and worktree; the branch note reports `Runner error (landing)` with the timeout detail and the worktree log shows the `landing check` timeout, not the pre-review `check`.

## Plan

Add strict timeout configuration and propagate it through runner command paths; share process-tree cleanup, add real-process and routing regression coverage, verify with the deadline disabled, then format and run checks.

## Notes

Suggestion origin: chitty

Planner, 2026-11-19: written against `_run_logged` from `TASK-353` and `TASK-426`, which have not landed (`TASK-353` is still in planning). Keep this ticket in `planning`; once `TASK-426` is `done`, check the description against `src/chitty/run.py`, cold-read again, then move it to `todo`.

Cold read 2026-11-21 outcomes: named the phase strings `setup`, `check` and `landing check`; said where the timeout value comes from (`main_repo.config`, passed through `_setup`, `_landing_check` and `_run_check`); criterion 5 accepts a failed `assertRaises`, since the old code returns normally; the hanging command records its own and its child PID as `tests/test_run_timeout.py` does; Docker containers left running by a killed `docker run` are out of scope. Still waits for `TASK-426` (which waits for `TASK-353`, in review): once `TASK-426` is `done`, compare with what landed, cold-read again, then move to `todo`.

Partial implementation: added and tested command_timeout configuration; make check passes. Runner enforcement, documentation, real-process tests and deadline-disabled regression evidence remain unfinished. Do not treat the configuration alone as implementing the timeout.

Deadline-disabled regression run: all five new timeout cases failed as expected. The direct case did not raise CommandTimedOut; setup and check cases ran the agent instead of returning todo to error; doing lacked the timeout note; landing returned review to done instead of done to error. Restored wait timeout afterward.

Reviewed: `make check` passed (983 tests; ruff and pyright clean). The worker recorded the deadline-disabled regression run in the preceding note; all five timeout cases failed and passed after restoration.
1: pass - `tests.test_config.TestRepoConfig` property and type/default tests passed in `make check`; executing them with `main`'s `RepoConfig` produced two errors, including missing `command_timeout` and failure to reject -1.
2: pass - `tests.test_command_timeout.TestCommandTimeout.test_logged_timeout_and_disabled_timeout` passed in `make check`; the recorded deadline-disabled run failed because `CommandTimedOut` was not raised.
3: pass - `tests.test_command_timeout.TestCommandTimeoutRouting` passed in `make check`; the recorded deadline-disabled run ran the agent for both todo cases and omitted the doing timeout note.
4: pass - `tests.test_review_merge.TestReviewMerge.test_landing_check_timeout_records_error_without_advancing_main` passed in `make check`; the recorded deadline-disabled run returned review to done rather than done to error.

## Summary

Implemented per-command setup and check deadlines with shared process-tree cleanup and existing failure routing. Added configuration property coverage, real-process cleanup and routing tests, and documented the one-hour default. All five timeout regression cases failed with the deadline disabled and passed after restoration; make check passed (983 tests). No follow-ups.

## History

- 2026-11-19T20:55:24Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:25Z sunny-white-dormouse: changed notes
- 2026-11-19T21:03:18Z sunny-white-dormouse: changed labels, priority, dependencies, description, acceptance criteria
- 2026-11-19T21:03:18Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:04:02Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:04:59Z sunny-white-dormouse: changed description, acceptance criteria, notes
- 2026-11-19T21:04:59Z sunny-white-dormouse cold-read → planning
- 2026-11-21T07:57:26Z nimble-umber-gannet: changed description
- 2026-11-21T07:57:26Z nimble-umber-gannet planning → cold-read
- 2026-11-21T07:58:40Z nimble-umber-gannet: changed description, acceptance criteria, notes
- 2026-11-21T07:58:40Z nimble-umber-gannet cold-read → planning
- 2026-11-21T16:02:43Z honest-coral-heron: changed description, acceptance criteria
- 2026-11-21T16:02:43Z honest-coral-heron planning → cold-read
- 2026-11-21T16:06:58Z honest-coral-heron cold-read → planning
- 2026-11-21T16:07:01Z honest-coral-heron planning → todo
- 2026-11-21T16:09:52Z golden-bronze-marten todo → doing
- 2026-11-21T16:12:23Z golden-bronze-marten: wrote the plan
- 2026-11-21T16:15:58Z golden-bronze-marten: changed notes
- 2026-11-21T16:19:34Z golden-bronze-marten: changed notes
- 2026-11-21T16:22:59Z golden-bronze-marten: changed summary
- 2026-11-21T16:23:02Z golden-bronze-marten doing → review
- 2026-11-21T16:29:30Z plucky-white-eel: changed notes
- 2026-11-21T16:29:30Z plucky-white-eel review → done
