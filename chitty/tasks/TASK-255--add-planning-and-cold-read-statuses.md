---
title: Add planning and cold-read statuses
status: backlog
labels:
  - plan-next
created: 2026-11-11
---

## Description

- New flow: `backlog` → `planning` → `cold-read` → `planning` → `todo` → `review` → `done`.
- `backlog`: triaged now and then; much of it gets thrown away.
- `planning`: active ticket writing.
- `cold-read`: `chitty run` picks it up, runs the cold-read role in a worktree, keeps the commit at `refs/cold-read/<ID>/<n>`, writes the report there, and moves the ticket back to `planning`. Never straight to `todo`.
- Open: what the report file is called, and whether `chitty list` hides `backlog` by default.
- Open, from archived TASK-70 and TASK-74: whether dependency waits become a derived `queued` flag (🔒) and `blocked` a `blocked_by` flag (⛔), so statuses run in one line in the direction of travel. The human chose those names and glyphs on 2026-11-08.

## History

- 2026-11-11T10:02:51Z jolly-heron → backlog
- 2026-11-11T10:18:43Z vivid-yellowhammer: changed description
