---
title: Pin the test fixture config to the runner workflow
status: doing
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

- [ ] A repository written from `CONFIG` in `tests/support.py`, with its `chitty_version` rewritten to `"0.5.0"`, loads through `load_repo_config` with `config.workflow == "runner"` and `config.review is True`. Fails before the change (`'tickets' != 'runner'`).
- [ ] `make check` passes, and also passes with `__version__` in `src/chitty/__init__.py` temporarily set to `0.5.0` (restore it afterwards; do not commit the change).

## Notes

Cold read starting point: `refs/cold-read/TASK-335/1` (on top of TASK-330's read). Its files: `tests/support.py`, `tests/test_config_workflow.py`; see them with `git show refs/cold-read/TASK-335/1:<path>`. Rebase onto the real TASK-330 on `main`, whose test file may differ, and check against the current criteria. At `0.5.0` without the fix, these failed: `TestReviewStatus` (two tests) in `tests/test_cli.py`, `TestRepoConfig.test_loads`, and `TestMcp.test_adds_backlog_without_a_description`.

## History

- 2026-11-14T18:46:23Z friendly-ginger-adder → planning
- 2026-11-14T18:46:39Z friendly-ginger-adder: changed owner
- 2026-11-14T18:46:39Z friendly-ginger-adder planning → cold-read
- 2026-11-14T18:50:04Z friendly-ginger-adder: changed description, acceptance criteria, notes
- 2026-11-14T18:50:04Z friendly-ginger-adder cold-read → planning
- 2026-11-14T18:50:06Z friendly-ginger-adder: changed owner
- 2026-11-14T18:50:06Z friendly-ginger-adder planning → todo
- 2026-11-14T20:07:15Z rosy-indigo-lapwing todo → doing
