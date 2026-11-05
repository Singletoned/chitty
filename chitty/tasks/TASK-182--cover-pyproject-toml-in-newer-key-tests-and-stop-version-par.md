---
title: Cover `pyproject.toml` in newer-key tests, and stop version parsing failing reads
status: backlog
priority: low
parent: TASK-106
created: 2026-11-05
---

## Description

Two gaps left by `TASK-137`, both in `load_repo_config` in `src/chitty/config.py`.

Its criterion 1 asked for tests of either config file, but the tests only use `chitty.toml`. A manual run on 2026-11-05 showed `[tool.chitty]` behaving correctly: a newer version loads with the warning, and an equal version refuses. Add the test. It is a regression test, so expect it to pass before any change.

`_allow_newer_top_level_keys` also calls `_version_key` on every load, before it knows whether any key is unknown. `_version_key` only accepts dotted integers, so a repository recording `0.2.0rc1` now fails `chitty list` with `invalid Chitty version`. Before `TASK-137` only writes did. `.github/workflows/release.yml` accepts `rc`, `a` and `b` tags. Move the comparison after the check for unknown keys, so a file with no unknown keys never parses a version on a read. A malformed version in a file with unknown keys still raises `invalid Chitty version`, and one in a file without them now loads on a read, as it did before `TASK-137`. Writes keep their existing behaviour through `check_setup_version`.

Out of scope: supporting pre-release versions properly, including running an `rc` build of Chitty, and the string comparison in `_warn_setup_version`, which is `TASK-135`.

## Acceptance Criteria

- [ ] A test shows an unknown top-level key in `[tool.chitty]` loading with one stderr warning when `chitty_version` is newer, and refusing when it is equal

## History

- 2026-11-05T09:51:15Z mellow-newt → backlog
- 2026-11-05T09:53:17Z mellow-newt: changed description, acceptance criteria
