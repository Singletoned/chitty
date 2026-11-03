---
title: "`chitty --version` reports stale package metadata instead of the running code"
status: todo
created: 2026-11-03
---

## Description

`chitty --version` prints the installed package metadata, not the running code's version. `src/chitty/cli.py` uses `click.version_option(package_name="chitty")`, which reads `importlib.metadata`, so it goes stale in an editable install. On 2026-11-03 it printed 0.1.19 while `__version__` was 0.1.21. `TASK-83` moved `CHITTY_VERSION` to the code but missed this path. Pass `version=CHITTY_VERSION`, which is already imported in `cli.py`, and keep click's output format. Add the test to `tests/test_version.py`. The test must not hard-code a version number.

## Acceptance Criteria

- [ ] With `importlib.metadata.version` patched to return `0.0.0`, `chitty --version` prints exactly `chitty, version <CHITTY_VERSION>`; run before the fix, that test fails

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03: corrected a stale line number and version, and added the missing criterion, including a test that fails even when the metadata happens to be current.

## History

- 2026-11-03T11:27:23Z eager-raven → todo
- 2026-11-03T18:19:33Z lively-panda: changed description, acceptance criteria, notes
