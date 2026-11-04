---
title: Land the Pi token analysis
status: todo
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

The `pi-token-analysis` branch holds `docs/pi-token-usage.md`, which these tickets come from, and `scripts/`, which the later ones re-run to measure their savings. Nothing on `main` has either. The branch is checked out in `.worktrees/pi-token-analysis`, so cherry-pick its 5 commits onto the ticket's own branch, as usual. They add only new files. The scripts already pass `ruff`, and `pyright` covers only `src` and `tests`, so `make check` should need nothing. Leave `pi-token-analysis` and its worktree alone: `~/.envs/default` may still use them, so removing them is for the human. The doc's recommendations and "what not to do" stay as a record, with a line at its top naming these tickets.

## Acceptance Criteria

- [ ] `main` has `docs/pi-token-usage.md`, with a line at its top naming these tickets, and `scripts/`, and `make check` passes

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: how to take the commits, given the worktree, and a criterion that only this machine could show.

## History

- 2026-11-04T21:41:05Z mellow-newt → backlog
- 2026-11-04T21:44:19Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T21:44:20Z mellow-newt backlog → todo
