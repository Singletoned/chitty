---
title: Tell cold readers to implement, and planners not to promote on a probe
status: done
parent: TASK-284
created: 2026-11-11
---

## Description

- Haiku readers often probe instead of implementing, though `chitty guide cold-read` says to implement (TASK-284, from echonomicon).
- In `src/chitty/roles/cold-read.md`: implement the ticket unless probing has already found a problem that will change it; then say so and stop.
- In `src/chitty/roles/plan.md`: a read that only probed does not make a ticket ready; read it again. Only an implementing read whose tests failed first does. Also merge the two bullets there that both start "Cold-read every ticket, even a small one."

## Acceptance Criteria

- [x] A test in `tests/test_guide_cold_read.py` shows `chitty guide cold-read` saying to implement unless probing found a problem, and `chitty guide plan` saying a probe-only read does not make a ticket ready. It fails today.
- [x] `chitty guide plan` contains "Cold-read every ticket, even a small one" exactly once.

## Plan

Add a focused test in tests/test_guide_cold_read.py asserting cold-read tells readers to implement unless probing found a blocking problem, and plan guide says probe-only reads do not qualify. Run it before edits to confirm failure. Update the cold-read and planning role text, merging the duplicate “Cold-read every ticket, even a small one” bullets, then run the focused test and full format/check.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-298/1`. Check it against the current criteria; do not trust it.

The new guide test failed before the role-text change. Full make check passes after the implementation.

Reviewed: `make format && make check` passed: 503 Python tests and Node tests OK; format changed no files.
1: pass - `uv run python -m unittest tests.test_guide_cold_read -v` ran 4 tests, OK. Running the new test with both guide texts from `main` printed `FAILED (failures=1)`; the baseline probe-only assertion printed `False`.
2: pass - the focused test asserts the phrase occurs once and passed; the same count on `main` printed 2.

## Summary

Updated the cold-read and planning guides and added a regression test. Verified with make format && make check; the new test failed before the fix. No follow-up.

## History

- 2026-11-11T21:10:09Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:20Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:15:01Z vivid-yellow-raven: changed description
- 2026-11-11T21:15:02Z vivid-yellow-raven: changed acceptance criteria, notes
- 2026-11-11T21:15:02Z vivid-yellow-raven cold-read → todo
- 2026-11-11T22:01:25Z mellow-yellow-adder todo → doing
- 2026-11-11T22:01:44Z mellow-yellow-adder: wrote the plan
- 2026-11-11T22:04:57Z mellow-yellow-adder: changed notes, summary; ticked acceptance criteria
- 2026-11-11T22:04:57Z mellow-yellow-adder doing → review
- 2026-11-11T22:07:32Z intrepid-white-quail: changed notes; ticked acceptance criteria
- 2026-11-11T22:07:32Z intrepid-white-quail review → done
