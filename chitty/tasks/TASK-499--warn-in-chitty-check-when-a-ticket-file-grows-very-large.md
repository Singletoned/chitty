---
title: Warn in `chitty check` when a ticket file grows very large
status: backlog
created: 2026-11-21
---

## Description

TASK-378 grew to 112 KB on its branch (90 KB of Notes was `make check` output pasted by the runner on each session start, the "Check failed before this session" block in `src/chitty/run.py`), and every worker and cold reader had to read it all. TASK-353 moves that output to a log, but nothing flags a ticket that has grown past what an agent can read cheaply, whatever the cause. Suggest a `chitty check` warning above a size threshold (for example 20 KB, as a module constant), naming the largest section, so the planner trims it before the next session.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:58:03Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:04Z nimble-umber-gannet: changed notes
