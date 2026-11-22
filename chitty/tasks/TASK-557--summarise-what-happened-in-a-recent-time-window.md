---
title: Summarise what happened in a recent time window
status: backlog
created: 2026-11-22
---

## Description

Requested by the owner on 2026-11-21: "chitty needs a summary feature, where I can see what has happened in the last few hours."

Today, answering "what happened since this morning?" means piecing together `git log` on `main`, each ticket's `## History` lines, runner output in terminals, and per-ticket notes. An agent did this by hand on 2026-11-21, with ad hoc scripts. The data is already there: History lines are timestamped and name the actor and the transition, and landed work commits carry `Task:` trailers.

Possible shape, to be decided in planning: one read-only view (perhaps `chitty list --since 4h`, or a summary mode of `list`, rather than a new command, to keep the surface small), grouped by outcome:
- landed (`→ done`, plus the landing commit),
- returned to `planning` or moved to `error`/`blocked`, with the first line of the latest note (why),
- created, and
- still in flight.

It should read each ticket from its authoritative source (`TASK-378` and `TASK-480`), so in-flight tickets' branch History counts. Per-ticket counts of `doing → planning` returns would also show which tickets keep bouncing.

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:32Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
