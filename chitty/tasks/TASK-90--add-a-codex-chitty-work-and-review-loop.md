---
title: Add a Codex `/chitty` work and review loop
status: backlog
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

## History

- 2026-11-01 → backlog
