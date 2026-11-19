---
title: Fix flaky test_run_cases repair step (blocked v0.4.0 release)
status: backlog
created: 2026-11-19
---

## Description

In `tests/test_next.py` `TestNext.test_run_cases`, the step at line 1830 (`changed = self.run_cli("run", "--errors")` with `CHANGE=1`) failed once in CI with: `Error: repair agent left TASK-1 in invalid status error; expected review or blocked`. The fake agent should have rewritten `status: error` to `status: blocked` in the worktree task file and committed it, yet `_status_after_agent` in `src/chitty/run.py` still read `error` after an exit-0 session. Evidence: release run https://github.com/Singletoned/chitty/actions/runs/43591689504 (tag v0.4.0, commit f062916) failed in `make check`; the `Check` workflow run 43591692705 on the same commit passed. Locally it passes in 3 serial runs and 8 concurrent runs. Suspects: state leaking between tests in a shared unittest-parallel worker (`os.environ` changes), or the preceding `PI_SIGNAL` interrupted step leaving the worktree or ticket in a state that the next run resets. Note that `make release` runs the full suite again in CI, so any flake blocks a release; consider whether the release workflow should rely on the `Check` result for the same commit instead of rerunning it.

## Notes

Suggestion origin: chitty

Archived: fixed in `c22e3a6`; superseded by the version-tie suggestion, itself covered by `TASK-367`, `TASK-378` and `TASK-386`.

## History

- 2026-11-19T20:55:09Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:11Z sunny-white-dormouse: changed notes
- 2026-11-19T20:56:35Z sunny-white-dormouse: changed notes
