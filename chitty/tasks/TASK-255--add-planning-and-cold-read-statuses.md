---
title: Add planning and cold-read statuses
status: backlog
labels:
  - plan-next
created: 2026-11-11
---

## Description

- New flow: `backlog` → `planning` → `cold-read` → `planning` → `todo` → `review` → `done`. `doing` and `blocked` stay as they are.
- `backlog`: triaged now and then; much of it gets thrown away.
- `planning`: active ticket writing.
- `cold-read`: waiting for a cold read, which always returns the ticket to `planning`, never straight to `todo`.
- Out of scope: `chitty run` running the cold reads (TASK-259), and the `queued` and `blocked_by` flags (TASK-70, TASK-74).
- Open: whether `chitty list` shows `planning` and `cold-read` by default. It already hides `backlog`.

## History

- 2026-11-11T10:02:51Z jolly-heron → backlog
- 2026-11-11T10:18:43Z vivid-yellowhammer: changed description
- 2026-11-11T10:36:54Z vivid-yellowhammer: changed description
