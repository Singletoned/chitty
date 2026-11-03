---
title: Stop agents committing or resetting in the main checkout
status: todo
priority: high
created: 2026-11-03
---

## Description

The global `chitty` runs whatever the main checkout contains. On 2026-11-03 the TASK-107 worker committed its `doing` claim on `main` by mistake, then ran `git reset --hard` in the main checkout to undo it (Pi session `2026-11-03T10-42-23`). A branch switch in main would also change `chitty` for every repository. Find a guard that makes this fail loudly, for example a hook or a clearer claim flow. See `TASK-118`.

## Acceptance Criteria

- [ ] A worker that tries to implement or switch branches in the main checkout is stopped or warned loudly

## History

- 2026-11-03T11:39:03Z eager-raven → todo
