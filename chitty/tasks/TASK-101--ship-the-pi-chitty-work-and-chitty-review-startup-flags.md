---
title: Ship the Pi `--chitty-work` and `--chitty-review` startup flags
status: todo
priority: high
created: 2026-11-02
---

## Description

The human added `--chitty-review` and `--chitty-work` startup flags to the installed extension (`~/.pi` commits `5d3d1fd`, `fe90bbc`): each starts Pi directly in that mode via a shared `start(mode)` helper and `pi.registerFlag`. The shipped `src/chitty/integrations/pi/chitty.ts` lacks them, so `chitty init` refuses to run (local edits detected), as with `TASK-93`. Port them into the shipped extension so `init` installs a matching file.

## Acceptance Criteria

- [ ] The shipped extension registers `--chitty-work` and `--chitty-review`, matching the installed behaviour; Node tests cover the flag parsing
- [ ] `__version__` is bumped, and `chitty init` succeeds against the edited install (record its hash or match it exactly)
- [ ] `README.md` documents the flags

## History

- 2026-11-02 → todo
