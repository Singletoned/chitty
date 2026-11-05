---
title: "`chitty --version` reports stale package metadata instead of the running code"
status: done
created: 2026-11-03
---

## Description

`chitty --version` prints the installed package metadata, not the running code's version. `src/chitty/cli.py` uses `click.version_option(package_name="chitty")`, which reads `importlib.metadata`, so it goes stale in an editable install. On 2026-11-03 it printed 0.1.19 while `__version__` was 0.1.21. `TASK-83` moved `CHITTY_VERSION` to the code but missed this path. Pass `version=CHITTY_VERSION`, which is already imported in `cli.py`, and keep click's output format. Add the test to `tests/test_version.py`. The test must not hard-code a version number.

## Acceptance Criteria

- [x] With `importlib.metadata.version` patched to return `0.0.0`, `chitty --version` prints exactly `chitty, version <CHITTY_VERSION>`; run before the fix, that test fails

## Plan

1. Inspect the CLI version decorator and existing version tests. 2. Add a regression test that patches package metadata and first confirm it fails. 3. Pass the code-defined version to Click, then run the focused test and `make check`.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03: corrected a stale line number and version, and added the missing criterion, including a test that fails even when the metadata happens to be current.

Second pass over the cold read: nothing further to change. Keeping click's output format and using `tests/test_version.py` are already in the description, and the only other findings were the stale numbers and missing criterion already fixed.

Verified criterion 1: the new regression test failed before the fix with patched metadata reporting `cli, version 0.0.0`; it now passes as `chitty, version 0.1.24`. `make check` passes (220 tests).

Re-checked every criterion immediately before review: `uv run python -m unittest tests.test_version` passed (2 tests) and `make check` passed (220 Python tests plus Ruff, pyright, and Node tests). Ready for independent review.

Reviewed: criterion 1 passed independently: patched `importlib.metadata.version` returned `0.0.0` while `chitty --version` printed exactly `chitty, version 0.1.24`; `tests.test_version` and `make check` passed after a fresh `make install`.

## History

- 2026-11-03T11:27:23Z eager-raven → todo
- 2026-11-03T18:19:33Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T20:00:19Z lively-panda: changed notes
- 2026-11-04T14:32:39Z open-quail: wrote the plan
- 2026-11-04T14:32:39Z open-quail todo → doing
- 2026-11-04T14:37:08Z open-quail: changed notes; ticked acceptance criteria
- 2026-11-04T14:38:51Z open-quail: changed notes
- 2026-11-04T14:38:51Z open-quail doing → review
- 2026-11-04T15:09:22Z jolly-puffin: changed notes
- 2026-11-04T15:09:22Z jolly-puffin review → done
- 2026-11-05T14:44:52Z vivid-wren done → archived
