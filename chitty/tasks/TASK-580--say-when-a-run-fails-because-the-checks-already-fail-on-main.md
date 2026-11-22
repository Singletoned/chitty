---
title: Say when a run fails because the checks already fail on `main`
status: backlog
created: 2026-11-22
---

## Description

Seen in taidy on 2026-11-22. `chitty run` picked up taidy `TASK-21` (remove an unsupported `actionlint -quiet` flag) and moved it `doing` to `error` 3 seconds later, with the note "Runner error (check): check exited with status 2". The failing check was `make check`, which runs `taidy lint .` over taidy`s own `.github/workflows`, and that fails because of the very bug `TASK-21` fixes. So `main` fails its own checks, and every ticket the runner picks up will go to `error` the same way, without saying that `main` is the cause. Suggestion: when the check fails before any work is done, say plainly that `main` fails its configured checks, stop the run instead of marking each ticket `error`, and name the failing command. Optionally allow a ticket marked as the fix for a broken check to run anyway.

## Notes

Suggestion origin: taidy

## History

- 2026-11-22T13:16:26Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:26Z friendly-jade-stoat: changed notes
