---
title: Stop `chitty init` installing the Pi extension
status: backlog
labels:
  - needs-minor
depends_on:
  - TASK-278
parent: TASK-275
created: 2026-11-11
---

## Description

- `chitty init` installs `src/chitty/integrations/pi/chitty.ts` into `~/.pi/agent/extensions/`. Once no command loads it, stop installing it and remove it, keeping only what must be in a plugin.
- Open: whether anything must stay in a plugin.

## History

- 2026-11-11T13:21:35Z vivid-yellowhammer → backlog
