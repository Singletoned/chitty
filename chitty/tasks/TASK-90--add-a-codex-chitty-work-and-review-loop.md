---
title: Add a Codex `/chitty` work and review loop
status: backlog
labels:
  - needs-discussion
priority: low
depends_on:
  - TASK-87
created: 2026-11-01
---

## Description

Pi has a `/chitty work` and `/chitty review` loop (TASK-87). Codex should get the same, shipped from this repo and installed or updated by `chitty init` when Codex is present, using whatever extension point Codex offers (custom prompts, hooks or plugins; not yet investigated).

## Acceptance Criteria

- [ ] `/chitty work` and `/chitty review` loop in Codex until `chitty next` reports nothing for that mode
- [ ] `chitty init` installs or updates it only when needed, reporting what it changed
- [ ] `README.md` documents it

## Notes

Before this can make another agent work, two things must leave Pi: the worker and reviewer prompts, which only `src/chitty/integrations/pi/chitty.ts` holds, and `CHITTY_PI_SESSION_ID`, which `chitty run` sets on the `task-126` branch. `TASK-136` makes the command configurable and leaves these two.

## History

- 2026-11-01 → backlog
- 2026-11-04T09:39:38Z lively-panda: changed notes
- 2026-11-11T10:17:08Z vivid-yellowhammer: changed labels
