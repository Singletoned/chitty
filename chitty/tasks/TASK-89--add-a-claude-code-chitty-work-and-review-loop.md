---
title: Add a Claude Code `/chitty` work and review loop
status: backlog
priority: low
depends_on:
  - TASK-87
created: 2026-11-01
---

## Description

Pi has a `/chitty work` and `/chitty review` loop (TASK-87). Claude Code should get the same, shipped from this repo and installed or updated by `chitty init` when Claude Code is present: probably a plugin with a `/chitty` command and a Stop hook that continues while `chitty next` reports work, ending on 'NO MORE WORK'.

## Acceptance Criteria

- [ ] `/chitty work` and `/chitty review` loop in Claude Code until `chitty next` reports nothing for that mode
- [ ] `chitty init` installs or updates it only when needed, reporting what it changed
- [ ] `README.md` documents it

## Notes

Before this can make another agent work, two things must leave Pi: the worker and reviewer prompts, which only `src/chitty/integrations/pi/chitty.ts` holds, and `CHITTY_PI_SESSION_ID`, which `chitty run` sets on the `task-126` branch. `TASK-136` makes the command configurable and leaves these two.

## History

- 2026-11-01 → backlog
- 2026-11-04T09:39:37Z lively-panda: changed notes
