---
title: Mark conflicted tickets in `chitty list` instead of failing
status: backlog
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-20
---

## Description

Owner decision 2026-11-20: once `TASK-378` reads each ticket from one source, a ticket whose source cannot be chosen (diverged local and remote branches, or edited on both its branch and `main` since they split) makes `chitty list` fail. Instead, `chitty list` should list every other ticket as usual and show the conflicted ticket with a marker saying it is conflicted, so the conflict stays visible without stopping the listing. Plan once `TASK-378` lands: choose the glyph and its precedence among the existing markers, what `--json` reports, and whether the runner skips conflicted tickets.

## Notes

Triage 2026-11-25: merged TASK-10017. Seen on 2026-11-25: `TASK-FER4EB` changed on both `task-fer4eb` and `main` (a planner's hand edit on `main`, commit `19109451`, reverted in `334c2b4d`), and `chitty list` printed only that error and no tickets. Also suggested: `chitty edit` on `main` of a ticket that has its own branch could refuse, as it already does for numeric IDs, so the conflict cannot be made by hand.

## History

- 2026-11-20T11:10:11Z lively-bronze-crane → backlog
- 2026-11-25T22:32:49Z calm-ochre-quail: changed notes
