---
title: Check the usage log against a real session and document it
status: doing
priority: high
depends_on:
  - TASK-148
parent: TASK-106
created: 2026-11-04
---

## Description

Last part of the log designed in `TASK-127`. Run a real Pi session in a scratch repository and compare its log line with the sum in its session file. A difference of more than 5% means Pi is not recording some calls, so say what is missing rather than adjusting for it. `PLAN.md` and `README.md` then describe the log and say its costs are list prices.

Out of scope: any report, which is `TASK-111`.

## Acceptance Criteria

- [ ] A note records a real session's log line and session-file sum, and explains any difference
- [ ] `PLAN.md` and `README.md` describe the log and say its costs are list prices

## Plan

1. Inspect the existing usage-log implementation and documentation conventions.
2. Run a real Pi session in an isolated scratch repository, capture the usage-log line and session JSONL, and calculate the session-file total.
3. Document the measured comparison and explanation in the appropriate project docs, explicitly identifying costs as list prices.
4. Run the focused tests and full `make check`, then record verified criteria and handoff.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: a threshold. Rejected: naming which extension copy loads, because `chitty run` refreshes the installed one first.

## History

- 2026-11-04T15:11:31Z mellow-newt → todo
- 2026-11-04T15:17:34Z mellow-newt: changed description, notes
- 2026-11-05T18:20:16Z friendly-eel todo → doing
- 2026-11-05T18:20:28Z friendly-eel: wrote the plan
