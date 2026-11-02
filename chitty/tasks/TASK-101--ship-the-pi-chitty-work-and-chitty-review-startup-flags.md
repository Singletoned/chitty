---
title: Ship the Pi `--chitty-work` and `--chitty-review` startup flags
status: doing
priority: high
created: 2026-11-02
---

## Description

The human added `--chitty-review` and `--chitty-work` startup flags to the installed extension (`~/.pi` commits `5d3d1fd`, `fe90bbc`): each starts Pi directly in that mode via a shared `start(mode)` helper and `pi.registerFlag`. The shipped `src/chitty/integrations/pi/chitty.ts` lacks them, so `chitty init` refuses to run (local edits detected), as with `TASK-93`. Port them into the shipped extension so `init` installs a matching file.

## Acceptance Criteria

- [ ] The shipped extension registers `--chitty-work` and `--chitty-review`, matching the installed behaviour; Node tests cover the flag parsing
- [ ] `__version__` is bumped, and `chitty init` succeeds against the edited install (record its hash or match it exactly)
- [ ] `README.md` documents the flags

## Plan

Compare the installed Pi extension with the shipped source and port the shared startup-mode helper plus both flags exactly. Add focused Node tests for flag parsing, bump the package version because `init` must propagate the change, document the flags in `README.md`, and verify `chitty init` accepts the installed extension before running `make check` and `chitty fix`.

## Notes

Choice: when both startup flags are supplied, `--chitty-review` wins. Review mode is safer than accidentally selecting implementation work, and the precedence is cheap to change; it is documented beside the conditional and in `README.md`.

## History

- 2026-11-02 → todo
- 2026-11-02T11:01:33Z frosty-falcon todo → doing
- 2026-11-02T11:01:33Z frosty-falcon: wrote the plan
