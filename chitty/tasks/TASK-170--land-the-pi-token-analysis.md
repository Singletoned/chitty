---
title: Land the Pi token analysis
status: done
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

The `pi-token-analysis` branch holds `docs/pi-token-usage.md`, which these tickets come from, and `scripts/`, which the later ones re-run to measure their savings. Nothing on `main` has either. The branch is checked out in `.worktrees/pi-token-analysis`, so cherry-pick its 5 commits onto the ticket's own branch, as usual. They add only new files. The scripts already pass `ruff`, and `pyright` covers only `src` and `tests`, so `make check` should need nothing. Leave `pi-token-analysis` and its worktree alone: `~/.envs/default` may still use them, so removing them is for the human. The doc's recommendations and "what not to do" stay as a record, with a line at its top naming these tickets.

## Acceptance Criteria

- [x] `main` has `docs/pi-token-usage.md`, with a line at its top naming these tickets, and `scripts/`, and `make check` passes

## Plan

Cherry-pick the five commits from the existing pi-token-analysis worktree onto this branch, preserving its new documentation and scripts. Add the requested ticket line at the top of docs/pi-token-usage.md, run the repository checks, then record verification and move the ticket to review.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: how to take the commits, given the worktree, and a criterion that only this machine could show.

1: pass - docs/pi-token-usage.md names TASK-170–TASK-176, scripts/ is present, and make check passed.

Reviewed: criterion verified independently; the source pi-token-analysis worktree is unchanged.

## Summary

Cherry-picked the five commits from the untouched `pi-token-analysis` worktree, added the top-of-document `TASK-170`–`TASK-176` reference line, and left the source branch/worktree unchanged. Verified with `make check` (ruff, pyright, 277 Python tests, and npm tests; exit 0). `chitty fix` completed with pre-existing Markdown delimiter warnings.

## History

- 2026-11-04T21:41:05Z mellow-newt → backlog
- 2026-11-04T21:44:19Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T21:44:20Z mellow-newt backlog → todo
- 2026-11-05T23:00:15Z jolly-eel todo → doing
- 2026-11-05T23:00:27Z jolly-eel: wrote the plan
- 2026-11-05T23:09:23Z jolly-eel: ticked acceptance criteria
- 2026-11-05T23:09:31Z jolly-eel: changed summary
- 2026-11-05T23:09:31Z jolly-eel doing → review
- 2026-11-06T11:24:09Z kind-quail: changed notes
- 2026-11-06T11:24:09Z kind-quail review → done
