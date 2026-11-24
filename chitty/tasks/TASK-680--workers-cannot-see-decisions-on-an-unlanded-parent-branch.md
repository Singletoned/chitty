---
title: Workers cannot see decisions on an unlanded parent branch
status: backlog
created: 2026-11-24
---

## Description

In shelfpath, the umbrella `TASK-1` adopted the Shelf URL design in `DOMAIN_MODEL.md` on its `task-1` branch. That branch cannot land until its children are done. The worker on child `TASK-7` reads `main`, so it found "no existing Shelf URL precedent" and sent the ticket back to planning, which cost a run. Options: warn when a parent ticket's branch changes docs that are not on main, have `chitty run` tell a child worker about its parent's unlanded commits, or advise in `chitty guide plan` that umbrella tickets must not hold design docs their children need, and should land those separately through a `plan/` branch.

## Notes

Suggestion origin: shelfpath

## History

- 2026-11-24T22:21:43Z zesty-coral-newt → backlog
- 2026-11-24T22:21:44Z zesty-coral-newt: changed notes
