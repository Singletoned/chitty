---
title: Retry landing when main moves during the landing check
status: backlog
created: 2026-11-19
---

## Description

TASK-322 passed review, but `chitty run` moved it to `error` because `git merge --ff-only task-322` failed: other agents committed to `main` while `_land_locked` (`src/chitty/run.py`) ran setup and check after merging `main`. The landing lock only serialises landings, not other commits on `main`, so this race recurs whenever checks are slow. Suggest: when the fast-forward fails because `main` moved, merge `main` again and re-run checks a bounded number of times before recording an error. A planner had to send TASK-322 back to `review` (2026-11-14), costing a second review.

## Notes

Suggestion origin: chitty

Archived: already done; `_land_locked` (`src/chitty/run.py`) retries the rebase, setup, check and fast-forward up to `LANDING_ATTEMPTS` times when `main` moves (`tests/test_landing_retry.py`).

## History

- 2026-11-19T20:55:11Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:12Z sunny-white-dormouse: changed notes
- 2026-11-19T21:20:03Z sunny-white-dormouse: changed notes
