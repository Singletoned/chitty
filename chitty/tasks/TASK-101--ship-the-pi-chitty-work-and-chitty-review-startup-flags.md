---
title: Ship the Pi `--chitty-work` and `--chitty-review` startup flags
status: done
priority: high
created: 2026-11-02
---

## Description

The human added `--chitty-review` and `--chitty-work` startup flags to the installed extension (`~/.pi` commits `5d3d1fd`, `fe90bbc`): each starts Pi directly in that mode via a shared `start(mode)` helper and `pi.registerFlag`. The shipped `src/chitty/integrations/pi/chitty.ts` lacks them, so `chitty init` refuses to run (local edits detected), as with `TASK-93`. Port them into the shipped extension so `init` installs a matching file.

## Acceptance Criteria

- [x] The shipped extension registers `--chitty-work` and `--chitty-review`, matching the installed behaviour; Node tests cover the flag parsing
- [x] `__version__` is bumped, and `chitty init` succeeds against the edited install (record its hash or match it exactly)
- [x] `README.md` documents the flags

## Plan

Compare the installed Pi extension with the shipped source and port the shared startup-mode helper plus both flags exactly. Add focused Node tests for flag parsing, bump the package version because `init` must propagate the change, document the flags in `README.md`, and verify `chitty init` accepts the installed extension before running `make check` and `chitty fix`.

## Notes

Choice: when both startup flags are supplied, `--chitty-review` wins. Review mode is safer than accidentally selecting implementation work, and the precedence is cheap to change; it is documented beside the conditional and in `README.md`.

Reviewed: verified both startup flags and review precedence, Node tests, version 0.1.16, README documentation, and the shipped extension hash matches the installed copy.

## Summary

Ported the shared startup helper and `--chitty-work`/`--chitty-review` flags from the installed Pi extension, with review-mode precedence when both flags are supplied. Added explicit flag-value tests, bumped the package to `0.1.16`, and documented the flags. Reinstalled the matching extension with `chitty init` and verified it matches the shipped file. Ran `npm test`, `make check`, and `chitty fix` (existing repository warnings only).

## History

- 2026-11-02 → todo
- 2026-11-02T11:01:33Z frosty-falcon todo → doing
- 2026-11-02T11:01:33Z frosty-falcon: wrote the plan
- 2026-11-02T11:02:12Z frosty-falcon: ticked acceptance criteria
- 2026-11-02T11:03:04Z frosty-falcon doing → review
- 2026-11-02T11:22:25Z jolly-falcon: changed notes
- 2026-11-02T11:22:25Z jolly-falcon review → done
