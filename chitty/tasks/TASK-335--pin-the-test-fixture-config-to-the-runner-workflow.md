---
title: Pin the test fixture config to the runner workflow
status: cold-read
owner: friendly-ginger-adder
depends_on:
  - TASK-330
created: 2026-11-14
---

## Description

After TASK-330, a config with no `workflow` line resolves by its `chitty_version`: older than `0.5.0` is `runner`, otherwise `tickets`. The shared test config `CONFIG` in `tests/support.py` has no `workflow` line and records `chitty_version` as the installed `__version__`. So when the release raises `__version__` to `0.5.0`, every `RepoTestCase` repository silently becomes `tickets`, reviews default to off, and runner tests fail at release time, not before.

- Add `workflow = "runner"` to `CONFIG` in `tests/support.py`, since most tests exercise the runner pipeline.
- Add a test, in `tests/test_config_workflow.py`, that loads a repository written from `CONFIG` with `CHITTY_VERSION` patched to `"0.5.0"` (patch it where `tests/support.py` and the config loader read it) and asserts `config.workflow == "runner"` and `config.review is True`.
- No property test: one fixed config and one version.

## Acceptance Criteria

- [ ] With `CHITTY_VERSION` patched to `"0.5.0"`, a repository from `CONFIG` in `tests/support.py` loads with `config.workflow == "runner"` and `config.review is True`. Fails before the change.
- [ ] `make check` passes, and also passes with `__version__` in `src/chitty/__init__.py` temporarily set to `0.5.0` (restore it afterwards; do not commit the change).

## History

- 2026-11-14T18:46:23Z friendly-ginger-adder → planning
- 2026-11-14T18:46:39Z friendly-ginger-adder: changed owner
- 2026-11-14T18:46:39Z friendly-ginger-adder planning → cold-read
