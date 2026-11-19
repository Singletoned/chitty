---
title: Warn when a ticket branch reaches main before its review passes
status: backlog
created: 2026-11-19
---

## Description

On 2026-11-13 at 19:37 a hand-run session merged `task-318` into `main` ("Merge TASK-318 runner error fixes", `6a9e3ee`) while TASK-318 was still in review; it was blocked after a third failed review at 19:44. Its commit `44bca53` made every pre-session check failure move the ticket to `error` without starting the agent, so any `doing` ticket with unfinished, failing work can no longer resume (TASK-321 went `doing -> error` on 2026-11-14; TASK-329 fixes that). `chitty run` only fast-forwards after a pass, but nothing stops a hand-run merge. Suggest a deterministic check, e.g. in `chitty check` (run by `make check`): report any commit on `main` reachable from a `task-<id>` branch tip, or a merge commit naming one, whose ticket is not `done`.

## Notes

Suggestion origin: chitty

Archived as covered by `TASK-358`.

## History

- 2026-11-19T20:55:27Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:28Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:00Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:04Z sunny-white-dormouse backlog → archived
