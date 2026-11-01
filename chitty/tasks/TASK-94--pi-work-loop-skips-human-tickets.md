---
title: Pi work loop skips `human` tickets
status: todo
priority: high
created: 2026-11-01
---

## Description

The `/chitty work` loop treats `human` tickets as its own: `isActionableTicket` counts any `todo`/`doing` ticket, and the prompt says to select `todo` or `doing`. A Pi agent therefore picked up HUMAN-4, HUMAN-5 and HUMAN-7, could not do them, and set them `blocked`, which hid them from people and left nothing actionable. Human tickets wait for a person in `todo`; agents should leave them alone.

## Acceptance Criteria

- [ ] `hasActionableTickets` in work mode ignores tickets whose `context` is `human`, with a test
- [ ] The work prompt tells agents not to select or change `human` tickets
- [ ] The managed guide block says agents leave `human` tickets for people and never block them, with a version bump

## History

- 2026-11-01 → todo
