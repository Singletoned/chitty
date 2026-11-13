---
title: Preserve agent output on timeout
status: todo
parent: TASK-318
created: 2026-11-13
---

## Description

The review of `TASK-318` found that `_run_session` in `src/chitty/run.py` drops captured output on agent timeout: `sh -c 'echo TIMEOUT_MARKER; sleep 5'` with a one-second timeout reports only the timeout. Preserve all output captured before termination in the timeout error and resulting ticket error handoff, alongside the timeout duration. Keep existing timeout and ticket-state behavior. Add a real-subprocess regression that prints a marker, times out, and checks the error note; run it before the fix and record failure. This needs a real process and timeout; no pure function can test the capture and termination boundary.

## Acceptance Criteria

- [ ] A fake agent prints `TIMEOUT_MARKER` and times out; its ticket enters `error`, and the recorded error includes both the marker and timeout duration. The regression fails before the fix and passes after it.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-324/1`. Check it against the current criteria; do not trust it.

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
