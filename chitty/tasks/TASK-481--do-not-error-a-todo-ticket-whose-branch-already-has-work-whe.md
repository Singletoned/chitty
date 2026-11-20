---
title: Do not error a `todo` ticket whose branch already has work when the pre-session check fails
status: backlog
created: 2026-11-20
---

## Description

On 2026-11-20 TASK-474 went back from `planning` to `todo` after a planner settled a worker question. Its branch already held the worker's committed partial implementation and a test still expected to fail. The runner's pre-session `check` failed on that test, and because the ticket was `todo` it went to `error` with no agent (the rule in `docs/plan/next-action-and-runner.md`: a check failure on `todo` errors, on `doing` starts the agent). The planner had to set it to `doing` by hand. Either the planning guide should say to resume a ticket with committed work as `doing`, or the runner should treat a `todo` ticket whose branch has commits beyond `main` like `doing`.

Seen again 2026-11-20 on TASK-479: re-planned after its worker found the design broke `test_reports_every_problem`, moved to `todo`, then sent to `error` within a minute by the pre-session check failing on that same earlier implementation (commit `a60c5c9d`), with the full `make check` output pasted into its notes. Set to `doing` by hand. Any ticket returned to planning with committed work on its branch hits this.

## Notes

Suggestion origin: chitty

## History

- 2026-11-20T23:09:59Z quick-pearl-lapwing → backlog
