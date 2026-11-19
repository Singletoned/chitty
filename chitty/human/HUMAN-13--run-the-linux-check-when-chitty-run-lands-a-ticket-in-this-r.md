---
title: Run the Linux check when `chitty run` lands a ticket in this repository
status: planning
depends_on:
  - TASK-429
  - TASK-430
created: 2026-11-19
---

## Description

After `TASK-429` (`scripts/check_linux.sh`) and `TASK-430` (the `landing_check` setting) land, make every landing in this repository run `make check` in a Linux container, so Linux-only failures such as those that broke `v0.6.0` on 2026-11-19 surface on landing rather than at release.

Add `landing_check = "sh scripts/check_linux.sh"` to `chitty.toml` on the line after `check = "make check"` (before the first `[table]`). A ticket branch that changes `chitty.toml` cannot land through `chitty run`, and fixes are not made directly on `main`, so use a plain (non-ticket) worktree: `git worktree add -b linux-landing-check .worktrees/linux-landing-check main`, edit and commit there (`Run the Linux check on landing`), run `make check` there, then in the main checkout `git merge --ff-only linux-landing-check`, and remove the worktree and branch.

Docker must then be running on any machine that runs `chitty run` here; without it every landing fails with the `docker` error and the ticket goes to `error`. That is intended: the check never skips.

## Acceptance Criteria

- [ ] `git show main:chitty.toml | python3 -c "import sys, tomllib; print(tomllib.load(sys.stdin.buffer)[\"landing_check\"])"` prints `sh scripts/check_linux.sh`
- [ ] On a machine with Docker running, while `chitty run` lands a ticket, `docker ps --filter ancestor=chitty-linux-check` lists a running container (the image `TASK-429`'s script builds), and that ticket lands on `main`

## History

- 2026-11-19T18:44:12Z daring-amber-kestrel → planning
- 2026-11-19T18:44:24Z daring-amber-kestrel: changed acceptance criteria
- 2026-11-19T18:44:29Z daring-amber-kestrel planning → cold-read
- 2026-11-19T18:45:04Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T18:45:04Z daring-amber-kestrel cold-read → planning
