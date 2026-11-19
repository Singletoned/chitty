---
title: Run the Linux check when `chitty run` lands a ticket in this repository
status: cold-read
depends_on:
  - TASK-429
  - TASK-430
created: 2026-11-19
---

## Description

After `TASK-429` (`scripts/check_linux.sh`) and `TASK-430` (the `landing_check` setting) land, make every landing in this repository run `make check` in a Linux container, so Linux-only failures such as those that broke `v0.6.0` on 2026-11-19 surface on landing rather than at release.

In the main checkout, on `main`, add `landing_check = "sh scripts/check_linux.sh"` to `chitty.toml` on the line after `check = "make check"` (before the first `[table]`), and commit it with the message `Run the Linux check on landing`. `chitty.toml` changes only on `main`: a ticket branch that changes it cannot land.

Docker must then be running on any machine that runs `chitty run` here; without it every landing fails with the `docker` error and the ticket goes to `error`. That is intended: the check never skips.

## Acceptance Criteria

- [ ] `git show main:chitty.toml` contains `landing_check = "sh scripts/check_linux.sh"` at the top level
- [ ] While `chitty run` lands the next ticket, `docker ps --filter ancestor=chitty-linux-check` lists a running container, and the ticket lands (or, if the Linux check fails, its note shows `landing check exited` with the failing tests)

## History

- 2026-11-19T18:44:12Z daring-amber-kestrel → planning
- 2026-11-19T18:44:24Z daring-amber-kestrel: changed acceptance criteria
- 2026-11-19T18:44:29Z daring-amber-kestrel planning → cold-read
