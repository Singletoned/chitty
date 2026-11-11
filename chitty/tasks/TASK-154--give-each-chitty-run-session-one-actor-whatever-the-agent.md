---
title: Give each `chitty run` session one actor, whatever the agent
status: done
priority: high
created: 2026-11-04
---

## Description

`run` in `src/chitty/run.py` sets `CHITTY_PI_SESSION_ID` to a new UUID, which only works for Pi. A Claude Code agent sets its own `CLAUDE_CODE_SESSION_ID`, which `actor()` in `src/chitty/actor.py` checks ahead of the Pi variable, so the claim would be recorded under one name and the agent's writes under another.

Have `run` set `CHITTY_ACTOR` instead, to the readable name made from the new UUID, using a small public function in `src/chitty/actor.py` that calls `_readable_name` with the source `CHITTY_RUN`. `actor()` checks it first, so the claim, the agent, and anything the agent starts all record one name, with any agent. `run` already removes an inherited `CHITTY_ACTOR`, so two runs still differ. Stop setting `CHITTY_PI_SESSION_ID` in `run`. The Pi extension's own use of it for sessions started by hand stays.

The two-run test in `tests/test_next.py` reads `CHITTY_PI_SESSION_ID` and must change. Names can collide, 1 time in 625, so it must not compare names from random UUIDs, which is how `TASK-126` ended up with a test that could fail by chance: fix the UUIDs it uses, so the result is certain.

Out of scope: `TASK-146`'s question of how names are made, and anything specific to one agent.

## Acceptance Criteria

- [x] A test with a fake agent that sets its own `CLAUDE_CODE_SESSION_ID` shows the claim and a write from that agent recording one actor
- [x] A test with fixed UUIDs shows two runs giving their agents different `CHITTY_ACTOR` values, and neither setting `CHITTY_PI_SESSION_ID`

## Plan

1. Inspect actor/run implementations and existing run tests.
2. Add a public run-actor naming helper and have run set only CHITTY_ACTOR.
3. Add/update deterministic tests covering Claude session identity and two fixed UUID runs.
4. Run focused tests, then make check and verify all criteria before review.

## Notes

Cold read by a fresh Sonnet subagent with `TASK-155`, 2026-11-04. Fixed: the helper and its source; the existing test that breaks; a test that would have failed by chance; and the dependency on `TASK-136`, which was not needed, so this can go first. Rejected: the `chitty guide` hint appearing in a run-started Pi, because the extension still sets `CHITTY_PI_SESSION_ID` at session start. A subagent sharing its parent's actor, which is the existing design. Name collisions, which are `TASK-146`; a collision gives a loud refusal with an override. Moved to `todo` now the findings have outcomes.

Reviewed: acceptance criteria verified. The fake Claude-session agent records its claim and write under the same CHITTY_ACTOR; fixed UUID runs use distinct actors and leave CHITTY_PI_SESSION_ID unset. Focused tests passed; make check passed (247 Python tests and Node tests).

## Summary

Implemented the run-scoped actor identity. `chitty run` now derives `CHITTY_ACTOR` from a fresh UUID with the `CHITTY_RUN` source and no longer sets `CHITTY_PI_SESSION_ID`; the actor remains consistent through Claude Code child writes. Updated tests cover Claude-owned session IDs and deterministic distinct UUIDs. Verified focused tests and `make check` (247 Python tests and Node tests passed). `chitty fix` completed with existing markdown delimiter warnings only.

## History

- 2026-11-04T15:38:27Z mellow-newt → backlog
- 2026-11-04T15:40:06Z mellow-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-04T15:40:06Z mellow-newt backlog → todo
- 2026-11-05T16:43:54Z plucky-newt todo → doing
- 2026-11-05T16:44:08Z plucky-newt: wrote the plan
- 2026-11-05T16:50:49Z plucky-newt: ticked acceptance criteria
- 2026-11-05T16:50:51Z plucky-newt: ticked acceptance criteria
- 2026-11-05T16:50:59Z plucky-newt: changed summary
- 2026-11-05T16:50:59Z plucky-newt doing → review
- 2026-11-05T16:56:17Z open-stoat: changed notes
- 2026-11-05T16:56:17Z open-stoat review → done
- 2026-11-11T10:17:25Z vivid-yellowhammer: changed parent
