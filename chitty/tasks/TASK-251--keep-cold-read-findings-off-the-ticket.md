---
title: Keep cold-read findings off the ticket
status: review
created: 2026-11-10
---

## Description

Readers see earlier reads' findings in Notes, which likely biases them, and per-read notes bloat tickets that workers read.

Change the guides in `src/chitty/roles/`:

- `cold-read.md` (line 9): read only the Description and Acceptance Criteria; skip Notes, which may hold earlier reads' findings.
- `plan.md` (line 26): fix or reject each finding in the ticket text, and give the outcomes in your reply, not in a ticket note.
- `plan.md` (line 29): drop the "replace its notes once reads converge" bullet; with no per-read notes there is nothing to replace.
- Keep the one note `plan.md` allows at line 42, pointing the worker at a kept read as a starting point.

Put the tests in `tests/test_guide_cold_read_notes.py`, checking the printed guides (`chitty guide cold-read TASK-1`, `chitty guide plan`). `tests/test_guide_set_notes.py` asserts the removed bullet's wording; remove that test.

## Acceptance Criteria

- [x] `chitty guide cold-read <ID>` tells the reader to skip Notes, and `chitty guide plan` says to give finding outcomes in the reply, not a ticket note.
- [x] `chitty guide plan` no longer tells planners to replace notes once reads converge, and still describes the starting-point note.

## Plan

Update the cold-read and planning role guides to keep earlier findings out of ticket Notes, and replace the removed wording test with focused printed-guide tests. Verify the new tests fail before the guide changes, then run formatting and the full check suite.

## Notes

Possible starting point: `refs/cold-read/TASK-251/1` (`git show refs/cold-read/TASK-251/1:<path>`). Check it against the criteria; don't trust it.

New printed-guide tests failed before the guide updates (2 failures; Ran 4 tests, failures=2). After the changes, make check passed, including all 454 Python tests and Node tests.

## Summary

Updated the cold-read and planning guides, replaced the wording test with printed-guide regression coverage, and removed the obsolete set-notes test. Verified with make format and make check; focused regression tests failed before the guide changes and passed in the full suite. No follow-ups.

## History

- 2026-11-10T21:58:44Z jolly-heron → backlog
- 2026-11-10T22:00:41Z jolly-heron: replaced notes; changed description
- 2026-11-10T22:00:41Z jolly-heron backlog → todo
- 2026-11-10T22:32:09Z able-eel todo → doing
- 2026-11-10T22:32:28Z able-eel: wrote the plan
- 2026-11-10T22:34:52Z able-eel: changed notes, summary; ticked acceptance criteria
- 2026-11-10T22:34:52Z able-eel doing → review
