---
title: Flag tickets that are out of date on this branch in chitty list
status: backlog
depends_on:
  - TASK-602
created: 2026-11-23
---

## Description

Decided with the person, 2026-11-23: `chitty list` never refuses because a ticket is out of date on the current branch; it flags those tickets instead. Agents on branches rarely run `list`, so the flag is for a person looking at a branch.

Depends on `TASK-602`, which adds `Repo.branch_conflict(task_id) -> str | None` (the message a single-ticket command on that ticket would refuse with) and keeps listing from refusing.

To be planned: after the listing, one stderr line per listed ticket with a conflict, `warning: <conflict>`, in id order, like the existing broken-dependency warning; stdout and `--json` unchanged. Tests: a real-Git case on a branch behind `main` for one ticket, asserting the warning line and an unchanged stdout.

## History

- 2026-11-23T08:22:18Z plucky-umber-wren → todo
- 2026-11-23T08:22:38Z plucky-umber-wren todo → backlog
