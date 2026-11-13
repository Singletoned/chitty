---
title: Accept native Pi identity without an extension warning
status: done
parent: TASK-275
created: 2026-11-13
---

## Description

The warning in `src/chitty/actor.py` and `src/chitty/cli.py` says Pi needs the Chitty extension even when native `PI_SESSION_ID` supplies an identity. Align the warning with `actor()` and give an actionable `CHITTY_ACTOR` remedy when identity is missing. Keep existing actor precedence and do not change the extension or runner. Use Hypothesis to generate nonempty and whitespace-only identity values for `PI_SESSION_ID`, `CHITTY_PI_SESSION_ID`, and `CHITTY_ACTOR` in Pi and non-Pi environments. Write regression tests first and record failures before the fix.

## Acceptance Criteria

- [x] Generated tests show native `PI_SESSION_ID` suppresses the warning, whitespace-only identities do not, and a genuinely missing Pi identity gets a warning that does not require the extension; the native ID test fails before the fix.

## Plan

Update the Pi missing-identity predicate to use the same trimmed identity precedence inputs as actor(), then replace the extension-specific guide warning with a CHITTY_ACTOR/native session-ID remedy. Expand the focused guide-warning tests with Hypothesis over nonempty and whitespace identities in Pi and non-Pi environments. First run the regression tests against current behavior and record the expected failure; then implement and verify.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-320/1`. Check it against the current criteria; do not trust it.

Regression-first evidence: `.venv/bin/python -m unittest tests.test_guide_pi_warning` failed before implementation. Hypothesis found PI_SESSION_ID="0" still considered missing; whitespace in CHITTY_PI_SESSION_ID was incorrectly treated as present; the old extension-only message also failed the revised expectations.

Hypothesis regression suite failed before the fix (including native PI_SESSION_ID and whitespace identities), then passed after the identity predicate and guide diagnostic were corrected. Full make check passes.

Reviewed:
1: pass - `uv run python -m unittest tests.test_guide_pi_warning` printed `Ran 7 tests` and `OK`; generated cases cover native, extension and actor identities and whitespace in Pi and non-Pi environments, and the guide test checks the remedy. Running the native generated test with `pi_session_environment_missing` loaded from `git show main:src/chitty/actor.py` printed `FAILED (failures=1)` with identity `0`; it passes on this branch. `make format && make check` passed (544 Python tests and Node tests).

## Summary

Implemented native Pi identity recognition and actionable missing-identity guidance. Verified with focused Hypothesis tests and full make check. No follow-ups.

## History

- 2026-11-13T22:24:26Z mellow-umber-lapwing → backlog
- 2026-11-13T22:24:49Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-13T22:24:49Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:25:07Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:25:07Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:26:24Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:26:24Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:32:39Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:32:39Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:36:42Z mellow-umber-lapwing: changed notes
- 2026-11-13T22:36:42Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:36:43Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:36:43Z mellow-umber-lapwing planning → todo
- 2026-11-13T22:38:29Z sunny-russet-gannet todo → doing
- 2026-11-13T22:38:51Z sunny-russet-gannet: wrote the plan
- 2026-11-13T22:39:12Z sunny-russet-gannet: changed notes
- 2026-11-13T22:41:51Z sunny-russet-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-13T22:41:51Z sunny-russet-gannet doing → review
- 2026-11-13T23:38:41Z tidy-amber-falcon: changed notes; ticked acceptance criteria
- 2026-11-13T23:38:41Z tidy-amber-falcon review → done
