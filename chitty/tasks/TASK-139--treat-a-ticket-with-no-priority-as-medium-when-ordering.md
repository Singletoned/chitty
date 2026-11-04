---
title: Treat a ticket with no priority as medium when ordering
status: todo
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Decided by the human on 2026-11-04: an unset priority should count as medium, not rank below low. Today `PRIORITY_ORDER` in `src/chitty/store.py` has `None: 3`, so `chitty next` and `chitty list` put an unprioritised ticket after a low one. Set `None` to the same rank as `medium`. Both users of `PRIORITY_ORDER`, `ordered` and `next_action`, then treat them alike, with their existing tie-breaks.

The field stays optional and `chitty list` still shows `-`: only the ordering changes. No version bump, since `chitty init` is not involved.

## Acceptance Criteria

- [ ] Tests show `chitty next` choosing an unprioritised ticket ahead of a low one, and by ID against a medium one, and `chitty list` ordering them the same way
- [ ] Any statement of priority ordering in `README.md` and `PLAN.md` matches

## History

- 2026-11-04T10:09:07Z lively-panda → todo
