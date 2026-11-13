---
title: Preserve agent output on timeout
status: review
parent: TASK-318
created: 2026-11-13
---

## Description

The review of `TASK-318` found that `_run_session` in `src/chitty/run.py` drops captured output on agent timeout: `sh -c 'echo TIMEOUT_MARKER; sleep 5'` with a one-second timeout reports only the timeout. Preserve all output captured before termination in the timeout error and resulting ticket error handoff, alongside the timeout duration. Keep existing timeout and ticket-state behavior. Add a real-subprocess regression that prints a marker, times out, and checks the error note; run it before the fix and record failure. This needs a real process and timeout; no pure function can test the capture and termination boundary.

## Acceptance Criteria

- [x] A fake agent prints `TIMEOUT_MARKER` and times out; its ticket enters `error`, and the recorded error includes both the marker and timeout duration. The regression fails before the fix and passes after it.

## Plan

Update the existing real-subprocess timeout integration test to print and flush a marker, then assert the resulting ticket error contains both the marker and timeout duration. Run that regression against the current implementation and record its failure. Preserve captured stdout when _run_session formats timeout errors, then run the focused test and the repository format/check commands. Commit only implementation/test files and hand off with verification evidence.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-324/1`. Check it against the current criteria; do not trust it.

Regression confirmed failing before the implementation: ticket error included the timeout duration but omitted TIMEOUT_MARKER. After the fix, the focused real-subprocess test passes. Full make format && make check passes.

## Summary

Handoff: timeout errors now retain captured agent stdout alongside the configured timeout duration; ticket error notes include both. The real-subprocess regression failed before the fix because TIMEOUT_MARKER was missing, and passes after. Verification: focused timeout test and make format && make check pass. Follow-up: none.

## History

- 2026-11-13T23:27:49Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:19Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-13T23:28:19Z mellow-umber-lapwing backlog → planning
- 2026-11-13T23:28:52Z mellow-umber-lapwing: changed owner
- 2026-11-13T23:28:52Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T23:31:23Z mellow-umber-lapwing: changed notes
- 2026-11-13T23:31:23Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T23:31:24Z mellow-umber-lapwing: changed owner
- 2026-11-13T23:31:24Z mellow-umber-lapwing planning → todo
- 2026-11-13T23:32:53Z vivid-fawn-wren todo → doing
- 2026-11-13T23:33:15Z vivid-fawn-wren: wrote the plan
- 2026-11-13T23:34:54Z vivid-fawn-wren: changed notes; ticked acceptance criteria
- 2026-11-13T23:35:04Z vivid-fawn-wren: changed summary
- 2026-11-13T23:35:04Z vivid-fawn-wren doing → review
