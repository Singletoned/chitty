---
title: Start every cold read through `chitty run`
status: backlog
depends_on:
  - TASK-272
parent: TASK-259
created: 2026-11-11
---

## Description

- `chitty guide cold-read` (`src/chitty/roles/cold-read.md`) drops the steps `chitty run` now does: creating the worktree, keeping `refs/cold-read/<ID>/<n>`, and removing the worktree. It tells the reader to write `.docs/cold-read/<ID>.md` and commit.
- `chitty guide plan` (`src/chitty/roles/plan.md`): set `-s cold-read`, poll until the ticket is back in `planning`, read the report with `git show cold-read/<id>/<n>:.docs/cold-read/<ID>.md`, then delete the branch once every finding has an outcome. The report is scratch and must never reach `main`.

## History

- 2026-11-11T13:21:10Z vivid-yellowhammer → backlog
