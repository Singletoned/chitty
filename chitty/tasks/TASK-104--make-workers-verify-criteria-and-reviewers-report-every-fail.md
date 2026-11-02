---
title: Make workers verify criteria and reviewers report every failure at once
status: todo
priority: high
created: 2026-11-02
---

## Description

`TASK-99` bounced through two failed reviews. The worker ticked all four criteria when two were unmet. Each reviewer then reported only the first failure it found, and the ticks stayed in place after both failures. Each round trip costs a full review, and the third failure blocks the ticket to a human.

## Acceptance Criteria

- [ ] The Pi work prompt (`chittyPrompt` and `continuationPrompt` in `src/chitty/integrations/pi/chitty.ts`) says to tick a criterion only after verifying it, and to re-check every criterion before setting `review`
- [ ] The Pi review prompt says to check every criterion, list every failure in one note, and `--uncheck` each failed criterion
- [ ] `src/chitty/guide.md` says the same, so non-Pi agents follow it
- [ ] Node tests cover the new prompt text, and `__version__` is bumped

## History

- 2026-11-02T13:03:21Z lively-otter → todo
