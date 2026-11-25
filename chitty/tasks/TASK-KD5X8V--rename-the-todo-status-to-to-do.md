---
title: Rename the `todo` status to `to-do`
status: backlog
labels:
  - needs-minor
created: 2026-11-25
provisional: true
---

## Description

Decided with the person, 2026-11-25: rename the `todo` status to `to-do`, to match `to-plan` (`TASK-10026`), so the waiting statuses read alike: `to-plan` / `planning`, `to-do` / `doing`.

To settle while planning: `chitty fix` migrating existing ticket files in every repository that uses Chitty, whether `todo` is still read (and for how long) so tickets on unlanded branches and older Chitty versions keep working, the `-s` choices and help text, the guides, runner prompts and messages, and `chitty.toml` or MCP values that name statuses. Plan it with `TASK-10026` and `TASK-599`, which also change the status set, so the migration machinery is built once.

## History

- 2026-11-25T23:00:35Z golden-coral-stoat → backlog
