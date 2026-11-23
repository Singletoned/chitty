---
title: Decide the rules for configurable statuses
status: backlog
labels:
  - untestable
owner: untestable
parent: TASK-607
created: 2026-11-23
---

## Description

Settle with the person, then record in `docs/plan/` (and update `docs/plan/non-goals.md`), the rules for configurable statuses before building them. Points to decide, with the suggestion's proposals:

- Workflows: custom statuses only with `workflow = "tickets"`; `workflow = "runner"` keeps the built-in set (or requires a superset), because the runner relies on `todo`, `doing`, `review`, `done`, `blocked`, `planning` and `error`.
- Which statuses count as finished for dependencies, `archive` and default `list` filtering, for example `closed_statuses = ["done", "dropped"]`.
- The status a new ticket gets, and how `-s` choices are validated once they come from config.
- List glyphs and five-letter abbreviations for custom statuses: derived, or set in config.
- How this relates to TASK-599 (a built-in `dropped` status).

Then split the build into small tickets under TASK-607.

## History

- 2026-11-23T10:40:43Z witty-russet-gannet → backlog
