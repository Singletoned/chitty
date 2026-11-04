---
title: Land the Pi token analysis
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

The `pi-token-analysis` branch holds `docs/pi-token-usage.md`, which these tickets come from, and `scripts/`, which the later ones re-run to measure their savings. Nothing on `main` has either. Rebase the branch onto `main`, make whatever `make check` needs of the scripts, and merge it. The worktree `.worktrees/pi-token-analysis` then goes, once the human has moved `~/.envs/default` off it (see `TASK-160`), so leave removing it to them. The doc's recommendations and "what not to do" stay as a record, with a line at its top naming these tickets.

## Acceptance Criteria

- [ ] `main` has `docs/pi-token-usage.md` and `scripts/`, `make check` passes, and `scripts/README.md`'s commands run from a checkout of `main`

## History

- 2026-11-04T21:41:05Z mellow-newt → backlog
