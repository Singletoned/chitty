---
title: Detect tickets overtaken by work committed straight to main
status: backlog
created: 2026-11-21
---

## Description

Evidence from echonomicon, 2026-11-19 (chitty 0.6.1). Between 14:25 and 14:38 a hand-run session committed five changes directly to `main`, with no `Task:` trailers: `0426d87` (player skip buttons, cleaned join playback), `d3a35e1` (removed words in partly cut lines), `5f317e0` (per-cut verdict forms on diagnostics), `d329ee1` and `022f1db` (review nav link). Together they implemented all or most of TASK-159, 160, 161, 163 and 164, but the tickets stayed `todo` or `error`. That evening `chitty run` gave them to work and repair agents, and those runs were wasted:
- TASK-161: the repair agent rewrote the feature as `a7feac7`, which conflicted with `d3a35e1` on rebase.
- TASK-160: a worker found the link "already implemented" and sent it to `planning`.
- TASK-164: a worker built a second `_join_button` that shadowed `main`s styled one, and review failed on the conflict.
- Detected by hand afterwards, from commit titles matching ticket titles.

Ideas, cheapest first:
1. Before starting a work or repair agent, run the ticket acceptance-criteria tests or check against `main`. If a criterion names a test that already exists and passes on `main`, say so in the agent prompt ("this may already be implemented on `main` by <commits>; verify first and, if so, send it to review").
2. List `main` commits since the ticket branch was made (or since the ticket last changed) that touch the files the ticket names, and put them in the work or repair prompt, so the agent starts by checking whether the work is done.
3. A `chitty` check or `next` warning when `main` has commits without a `Task:` trailer that touch files named in open tickets, so a planner can reconcile them before a run.
4. Tell hand-run sessions, in the work guide and generated AGENTS.md text, to claim the ticket (or add `Task:` trailers) when the work they do matches an open ticket. Commits on `main` then carry the link and chitty can see the ticket is done.

The work and repair guides should also say: if the ticket is already satisfied on `main`, set `review` with a note naming the commits, instead of reimplementing it or sending it to `planning`.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-21T07:57:44Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:46Z nimble-umber-gannet: changed notes
