---
title: Failed chitty edit still leaves the ticket written but uncommitted
status: backlog
labels:
  - bug
  - escape
created: 2026-11-17
---

## Description

Seen 2026-11-17 in the `task-364` worktree: `chitty edit TASK-364 --note ...` failed with `TASK-356 is used by more than one file` (see `TASK-367`), but the note had already been written to the ticket file, which was left modified and uncommitted. `TASK-355` (done) was meant to stop a failed `chitty edit` leaving its write uncommitted; this failure happens in the lookup during finalize, which `TASK-355` apparently does not cover. Source ticket: `TASK-355`.

## History

- 2026-11-17T20:00:43Z kind-umber-toad → backlog
