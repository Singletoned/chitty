---
title: Land tickets on an integration branch before `main`
status: backlog
created: 2026-11-21
---

## Description

Owner idea 2026-11-20, after a morning of half-states on `main`: the runner claimed tickets by committing on `main` while their branches already existed (`TASK-276` twice, `TASK-378`, `TASK-471`), so `main` held ticket states the branches lacked; reviews stopped on rebase conflicts in ticket files and workers were refused writes. A release or integration branch would gather landed tickets (and runner bookkeeping) before they reach `main`, so `main` only moves in checked batches. Questions to settle in planning: which branch the runner claims on and rebases onto, how `make release` relates to it, and whether `TASK-384` (claim on the ticket branch) and `TASK-370` (rebase before every work session) already remove most of the need.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:58:06Z nimble-umber-gannet → backlog
- 2026-11-21T07:58:07Z nimble-umber-gannet: changed notes
