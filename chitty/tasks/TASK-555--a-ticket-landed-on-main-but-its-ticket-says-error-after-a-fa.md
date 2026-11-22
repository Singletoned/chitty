---
title: A ticket landed on `main` but its ticket says `error` after a failed landing check
status: backlog
created: 2026-11-22
---

## Description

Seen 2026-11-22 on `TASK-540`. History: `review → done` at 04:03:31 by the review loop, then `done → error` at 04:05:03 with `Runner error (landing): landing check exited with status 2` (the check failed on a flaky test, since fixed by `TASK-553`). Yet the code is on `main` (commit `9027093c`, "Allow work rebase to stop on non-ticket conflicts", plus the ticket commit `ad7d201b` that records `error`), and the `task-540` branch and worktree are gone. So either the landing fast-forwarded `main` before (or despite) the failing check, or a later run landed the branch without updating the ticket. Result: a landed ticket stuck in `error`, its dependants blocked, and only a person can mark it `done` (a planner must not write the `Reviewed:` note). Worth checking the order in the landing code (`_land_locked` / `_land_pending` in `src/chitty/run.py`) and making a landed ticket end `done`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:31Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
