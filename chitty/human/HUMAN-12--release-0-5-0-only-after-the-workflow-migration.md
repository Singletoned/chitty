---
title: Release 0.5.0 only after the workflow migration
status: todo
depends_on:
  - TASK-331
  - TASK-335
created: 2026-11-14
---

## Description

TASK-330 makes a missing `workflow` resolve to `tickets` for configs recorded at `0.5.0` or later. Until TASK-331 lands, `chitty init` raises `chitty_version` without writing `workflow = "runner"`, so releasing `0.5.0` would turn every existing runner repository into a tickets one (reviews off, and after TASK-333 and TASK-334, `run`, `next` and the role guides hidden) on its next `init`. Until TASK-335 lands, the release check fails because the test fixture config resolves to `tickets` at `0.5.0`. Do not run `make release` while TASK-330 is on `main` and either of those is unfinished.

## Acceptance Criteria

- [ ] `make release` for `0.5.0` runs only after TASK-331 and TASK-335 are `done`.

## History

- 2026-11-14T18:46:35Z friendly-ginger-adder → todo
