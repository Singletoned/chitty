---
title: Make the Pi `/chitty` extension select work with `chitty next`
status: backlog
depends_on:
  - TASK-87
  - TASK-76
created: 2026-11-01
---

## Description

Once the extension lives here (TASK-87) and `chitty next` exists (TASK-76), the extension should stop parsing `chitty list --json` and status names itself and ask `chitty next --work` or `chitty next --review` instead, so status and flag changes (TASK-70, TASK-71, TASK-74) need no extension changes.

## Acceptance Criteria

- [ ] The extension's loop asks `chitty next` whether work remains and contains no status names
- [ ] Its tests cover both modes against a real repository

## Notes

Superseded for the pilot by `TASK-123`, which removes queue selection from the extension. Close this if `TASK-110` needs nothing more.

## History

- 2026-11-01 → backlog
- 2026-11-03T12:40:40Z lively-panda: changed notes
