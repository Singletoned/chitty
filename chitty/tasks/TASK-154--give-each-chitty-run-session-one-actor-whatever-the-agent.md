---
title: Give each `chitty run` session one actor, whatever the agent
status: backlog
priority: high
depends_on:
  - TASK-136
parent: TASK-106
created: 2026-11-04
---

## Description

`run` in `src/chitty/run.py` sets `CHITTY_PI_SESSION_ID` to a new UUID, which only works for Pi. A Claude Code agent sets its own `CLAUDE_CODE_SESSION_ID`, which `actor()` in `src/chitty/actor.py` checks ahead of the Pi variable, so the claim would be recorded under one name and the agent's writes under another.

Have `run` set `CHITTY_ACTOR` instead, to the readable name made from the new UUID. `actor()` checks it first, so the claim, the agent, and anything the agent starts all record one name, with any agent. `run` already removes an inherited `CHITTY_ACTOR`, so two runs still differ. Stop setting `CHITTY_PI_SESSION_ID` in `run`. The Pi extension's own use of it for sessions started by hand stays.

Out of scope: `TASK-146`'s question of how names are made, and anything specific to one agent.

## Acceptance Criteria

- [ ] A test with a fake agent that sets its own `CLAUDE_CODE_SESSION_ID` shows the claim and a write from that agent recording one actor
- [ ] A test shows two runs given different `CHITTY_ACTOR` values, compared as given to the agent

## History

- 2026-11-04T15:38:27Z mellow-newt → backlog
