---
title: Compare versions numerically in the stale setup warning
status: doing
labels:
  - bug
priority: medium
created: 2026-11-03
---

## Description

`_warn_setup_version` in `src/chitty/cli.py` compares `recorded < CHITTY_VERSION` as strings, so `0.1.9` counts as newer than `0.1.22` and the warning is lost. `store.py` already has a numeric `_version_key`. Use it here. Found by the `TASK-134` cold read.

Use `_version_key` from `src/chitty/store.py`, renaming it without the underscore now that two modules use it. It raises on a value such as `1.0rc1`, and this function runs on every command, so catch that here and warn that the recorded version cannot be read: a bad `chitty_version` should not stop reads. Writes already refuse it. Tests can use recorded values against the real version: `0.1.9` is older but sorts as newer, and `0.1.100` is newer but sorts as older.

## Acceptance Criteria

- [x] Tests, failing before the fix, show a numerically older recorded version asking to re-run `chitty init`, a numerically newer one asking to upgrade `chitty`, and an unreadable one warning without stopping a read

## Plan

1. Inspect the stale setup warning and existing version helper/tests.
2. Rename the shared numeric version helper in store.py and use it from cli.py, converting malformed recorded versions into a warning while preserving reads.
3. Add regression tests for numerically older, newer, and unreadable recorded versions; run the focused tests and full make check.
4. Record verification, check the criterion, and move the ticket to review.

## Notes

Moved back to `backlog` on 2026-11-04, under the new rule that a ticket stays there until its cold read has outcomes. A cold read is running.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the function's name; which helper to use; a bad version turning a warning into a crash on every read; and the newer direction, which has the same bug. Rejected: patching `CHITTY_VERSION` in tests, because recorded values can show both directions against the real one. Moved to `todo` now the findings have outcomes.

Reported again on 2026-11-04 by a session in another repository: a file recording `0.1.4` read as newer than `0.1.25`, so it told the person to upgrade Chitty rather than run `chitty init`, and misled the session. Raised to medium.

## Summary

Implemented numeric setup-version comparison in `src/chitty/cli.py`, reusing the shared `version_key` helper. Malformed recorded versions now emit a warning and reads continue; config loading no longer rejects them before the warning.

Verification: focused setup-version regression test and `make check` passed (269 Python tests and Node tests). Commit `d456459`.

## History

- 2026-11-03T21:24:19Z lively-panda → todo
- 2026-11-04T15:30:43Z mellow-newt: changed notes
- 2026-11-04T15:30:43Z mellow-newt todo → backlog
- 2026-11-04T15:31:49Z mellow-newt: changed description, notes
- 2026-11-04T15:31:49Z mellow-newt backlog → todo
- 2026-11-04T15:31:56Z mellow-newt: changed acceptance criteria
- 2026-11-04T21:00:15Z mellow-newt: changed priority, notes
- 2026-11-05T21:34:39Z sunny-jay todo → doing
- 2026-11-05T21:34:55Z sunny-jay: wrote the plan
- 2026-11-05T21:41:06Z sunny-jay: ticked acceptance criteria
- 2026-11-05T21:41:07Z sunny-jay: changed summary
