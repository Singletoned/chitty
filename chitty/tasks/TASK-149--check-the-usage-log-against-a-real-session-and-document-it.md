---
title: Check the usage log against a real session and document it
status: review
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

- [x] A note records a real session's log line and session-file sum, and explains any difference
- [x] `PLAN.md` and `README.md` describe the log and say its costs are list prices

## Plan

1. Inspect the existing usage-log implementation and documentation conventions.
2. Run a real Pi session in an isolated scratch repository, capture the usage-log line and session JSONL, and calculate the session-file total.
3. Document the measured comparison and explanation in the appropriate project docs, explicitly identifying costs as list prices.
4. Run the focused tests and full `make check`, then record verified criteria and handoff.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: a threshold. Rejected: naming which extension copy loads, because `chitty run` refreshes the installed one first.

Real Pi session verification (scratch repo `task149-scratch`, 2026-11-05): usage log line: `{"ticket":"TASK-1","mode":"work","actor":"brisk-zander","started":"2026-11-05T18:21:49.031890Z","seconds":33.828,"status_before":"doing","status_after":"review","models":[{"provider":"openai-codex","model":"gpt-5.6-luna","input":7645,"output":917,"cacheRead":32000,"cacheWrite":0,"cost":0.0032694}]}`. The corresponding session file `/Users/singletoned/.pi/agent/sessions/--private-tmp-chitty-task149-97lVKp-.worktrees-task-1--/2026-11-05T18-21-49-151Z_01a1acf2-16df-70f9-ad3a-cbdb55f9e135.jsonl` sums to `input=7645`, `output=917`, `cacheRead=32000`, `cacheWrite=0`, `cost=0.0032694`; difference is 0% (well below 5%), so no calls are missing. Costs are provider list prices.

## Summary

Documented the machine-local Pi usage JSONL log and list-price semantics in `PLAN.md` and `README.md`. Verified a real scratch-repository Pi session: the usage-log model totals exactly matched the session JSONL totals (`input=7645`, `output=917`, `cacheRead=32000`, `cacheWrite=0`, `cost=0.0032694`; 0% difference). `chitty fix` passed and `make check` passed (252 Python tests and Node tests). Existing unrelated Markdown delimiter warnings remain in other task files.

## History

- 2026-11-04T15:11:31Z mellow-newt → todo
- 2026-11-04T15:17:34Z mellow-newt: changed description, notes
- 2026-11-05T18:20:16Z friendly-eel todo → doing
- 2026-11-05T18:20:28Z friendly-eel: wrote the plan
- 2026-11-05T18:23:22Z friendly-eel: changed notes
- 2026-11-05T18:27:35Z friendly-eel: ticked acceptance criteria
- 2026-11-05T18:27:43Z friendly-eel: changed summary
- 2026-11-05T18:27:43Z friendly-eel doing → review
