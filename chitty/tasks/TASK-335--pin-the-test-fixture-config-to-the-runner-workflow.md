---
title: Pin the test fixture config to the runner workflow
status: done
depends_on:
  - TASK-330
created: 2026-11-14
---

## Description

After TASK-330, a config with no `workflow` line resolves by its `chitty_version`: older than `0.5.0` is `runner`, otherwise `tickets`. The shared test config `CONFIG` in `tests/support.py` has no `workflow` line and records `chitty_version` as the installed `__version__`. So when the release raises `__version__` to `0.5.0`, every `RepoTestCase` repository silently becomes `tickets`, reviews default to off, and runner tests fail at release time, not before.

- Add `workflow = "runner"` to `CONFIG` in `tests/support.py`, since most tests exercise the runner pipeline.
- Add a test class in `tests/test_config_workflow.py` that writes `CONFIG` into a temp repository with its `chitty_version` line rewritten to `"0.5.0"` (`CONFIG` is formatted at import, and `load_repo_config` reads only the file, so rewrite the text rather than patching `CHITTY_VERSION`), loads it with `load_repo_config` (not `Repo.open`, which refuses a recorded version newer than the installed one), and asserts `config.workflow == "runner"` and `config.review is True`.
- `TestWorkflowConfig` in that file (from TASK-330) inserts its own `workflow` line into `CONFIG`; once `CONFIG` has one, that gives a duplicate TOML key. Make its helper remove the `workflow = "runner"` line first.
- No property test: one fixed config and one version.

## Acceptance Criteria

- [x] A repository written from `CONFIG` in `tests/support.py`, with its `chitty_version` rewritten to `"0.5.0"`, loads through `load_repo_config` with `config.workflow == "runner"` and `config.review is True`. Fails before the change (`'tickets' != 'runner'`).
- [x] `make check` passes, and also passes with `__version__` in `src/chitty/__init__.py` temporarily set to `0.5.0` (restore it afterwards; do not commit the change).

## Plan

Pin the shared tests/support.py CONFIG to workflow = "runner". Update TestWorkflowConfig’s helper to remove that default line before inserting each workflow variant. Add the fixed-version regression test in tests/test_config_workflow.py: write CONFIG to a temporary repository with chitty_version rewritten to "0.5.0", load via load_repo_config, and assert runner workflow and reviews enabled. Run the regression test before implementation to confirm failure, then make format and make check; temporarily set __version__ to 0.5.0 for the second full check and restore it. Commit only intended implementation files with a Task: TASK-335 message, then update ticket verification and handoff.

## Notes

Cold read starting point: `refs/cold-read/TASK-335/1` (on top of TASK-330's read). Its files: `tests/support.py`, `tests/test_config_workflow.py`; see them with `git show refs/cold-read/TASK-335/1:<path>`. Rebase onto the real TASK-330 on `main`, whose test file may differ, and check against the current criteria. At `0.5.0` without the fix, these failed: `TestReviewStatus` (two tests) in `tests/test_cli.py`, `TestRepoConfig.test_loads`, and `TestMcp.test_adds_backlog_without_a_description`.

Regression test was run before the fixture change and failed as expected: workflow was tickets instead of runner. make check passed at the installed version and with __version__ temporarily set to 0.5.0; restored __version__ to 0.4.2 afterwards. Final make check passed. Commit: e9d3db0.

Review failed (work): The release-version check still fails; update the init test for the workflow selected at 0.5.0 and make the full release-version check pass. This is a newly discovered finding; there are no earlier review failures.
1: pass - `uv run python -m unittest tests.test_config_workflow.TestFixtureConfig` printed OK; removing the fixture workflow line first printed FAIL with `AssertionError: 'tickets' != 'runner'`.
2: fail - `make format && make check` passed at 0.4.2 (578 tests OK and Node tests passed). With `__version__` temporarily set to 0.5.0, `make check` printed FAILED (failures=1): `tests.test_cli.TestInit.test_init` expected `chitty guide work` in the generated AGENTS.md, but it was absent. The version was restored.

Fixed TestInit to assert the generated managed guide for resolve_workflow(None, CHITTY_VERSION), covering runner and tickets defaults. make format && make check passed at 0.4.2 and make check passed with __version__ temporarily set to 0.5.0; restored to 0.4.2. Commit 0264c3d.

Reviewed: Previous release-version failure is resolved; no new findings.
1: pass - `uv run python -m unittest tests.test_config_workflow.TestFixtureConfig` printed OK; removing the fixture workflow line printed FAIL with `AssertionError: 'tickets' != 'runner'`.
2: pass - `make format && make check` printed OK for 578 tests and passed Node tests at 0.4.2; `make check` with version temporarily set to 0.5.0 printed OK for 578 tests and passed Node tests. Version restored.

## Summary

Pinned the test fixture to runner and added the 0.5.0 regression test (prior commit e9d3db0). Updated TestInit expectations for version-selected managed guides (commit 0264c3d). Verification: make format && make check passed at installed 0.4.2; make check passed with __version__ temporarily set to 0.5.0; restored afterward. No follow-ups.

## History

- 2026-11-14T18:46:23Z friendly-ginger-adder → planning
- 2026-11-14T18:46:39Z friendly-ginger-adder: changed owner
- 2026-11-14T18:46:39Z friendly-ginger-adder planning → cold-read
- 2026-11-14T18:50:04Z friendly-ginger-adder: changed description, acceptance criteria, notes
- 2026-11-14T18:50:04Z friendly-ginger-adder cold-read → planning
- 2026-11-14T18:50:06Z friendly-ginger-adder: changed owner
- 2026-11-14T18:50:06Z friendly-ginger-adder planning → todo
- 2026-11-14T20:07:15Z rosy-indigo-lapwing todo → doing
- 2026-11-14T20:07:27Z rosy-indigo-lapwing: wrote the plan
- 2026-11-14T20:10:58Z rosy-indigo-lapwing: changed notes, summary; ticked acceptance criteria
- 2026-11-14T20:10:58Z rosy-indigo-lapwing doing → review
- 2026-11-14T20:20:48Z witty-ochre-quail: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-14T20:20:48Z witty-ochre-quail review → doing
- 2026-11-14T20:31:58Z rosy-amber-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-14T20:31:58Z rosy-amber-ibis doing → review
- 2026-11-14T20:36:28Z brisk-yellow-gannet: changed notes; ticked acceptance criteria
- 2026-11-14T20:36:28Z brisk-yellow-gannet review → done
