---
title: Pi work loop skips `human` tickets
status: done
priority: high
created: 2026-11-01
---

## Description

The `/chitty work` loop treats `human` tickets as its own: `isActionableTicket` counts any `todo`/`doing` ticket, and the prompt says to select `todo` or `doing`. A Pi agent therefore picked up HUMAN-4, HUMAN-5 and HUMAN-7, could not do them, and set them `blocked`, which hid them from people and left nothing actionable. Human tickets wait for a person in `todo`; agents should leave them alone.

## Acceptance Criteria

- [x] `hasActionableTickets` in work mode ignores tickets whose `context` is `human`, with a test
- [x] The work prompt tells agents not to select or change `human` tickets
- [x] The managed guide block says agents leave `human` tickets for people and never block them, with a version bump

## Plan

Filter `context == "human"` out of work-mode actionability in the Pi extension and say so in the work prompt; add one guide sentence; bump the patch version; Node tests first.

## Notes

Implemented by lively-otter (Claude Code). Regression test `leaves human tickets for people` failed before the fix; `node --test src/chitty/integrations/pi/tests/chitty.test.ts` and `make check` pass. `chitty init` could not install the new extension or refresh `AGENTS.md` because of the TASK-95 guard; the reviewer should re-run `chitty init` once that is resolved.

Reviewed: verified the human-context filter, work prompt and managed guide wording; Pi extension tests (12) and make check (183 tests) pass.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
