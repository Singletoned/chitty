---
title: Do not rerun the landing check when `main` moved only by ticket-file commits
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-19 at 21:05:50, `TASK-404` passed review and then failed to land: `Runner error (landing): main moved during each of the 3 landing attempts`. Between 21:01:42 and 21:05:49, `main` gained 7 commits, all but one of them `chitty: edit TASK-450/TASK-451` commits from a planning session, about one every 35 seconds. Each landing attempt in `_land_locked` (`src/chitty/run.py`) rebases, runs `setup` and the full landing check (about a minute), then tries `git.fast_forward`; `LANDING_ATTEMPTS` retries the whole cycle. While anyone is planning, ticket bookkeeping on `main` therefore beats every attempt. `TASK-428` does not help: it deliberately does not hold its lock during the landing check. Proposal: when the fast-forward fails, look at the commits `main` gained since the attempt's rebase. If every one of them changes only ticket files (paths under the configured context directories, such as `chitty/`), rebase onto the new `main` and fast-forward without rerunning `setup` or the check, because ticket files cannot change what the check tests. Rerun the full check only when a new commit touches anything else.

## Notes

Suggestion origin: chitty

Planner, 2026-11-21: duplicate of `TASK-468`, which landed and is `done`. Archive or delete this suggestion.

Triage 2026-11-24, merged from TASK-690: a landing by hand hits the same race. TASK-624's hand landing failed twice on 2026-11-23: during the 2-2.5 minute `make check`, other agents committed `chitty:` ticket edits to `main`, so `--ff-only` was refused. Whatever this ticket builds should be usable by a reviewer landing by hand too (see TASK-340).

## History

- 2026-11-21T07:57:51Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:52Z nimble-umber-gannet: changed notes
- 2026-11-21T08:05:24Z nimble-umber-gannet: changed notes
- 2026-11-24T22:40:00Z zesty-coral-newt: changed notes
