---
title: Renumber any ticket to the next number and rewrite references to it
status: to-plan
labels:
  - bug
created: 2026-11-24
---

## Description

In echonomicon (chitty 0.7.1), tickets added on a plan/ branch got provisional IDs (TASK-BCHE6A, TASK-VY5XWK). After fast-forwarding main, `chitty renumber chitty/tasks/TASK-BCHE6A--*.md` failed with 'TASK-BCHE6A is used by no other file; use `chitty move` to give it a new ID', and `chitty move TASK-BCHE6A tasks` failed with 'TASK-BCHE6A is already in context tasks'. renumber's help says it renumbers provisional tickets on main, so either renumber should accept a provisional ID with no clash on main, or move should allow the same context. Today there is no way to do it, so the planner kept the provisional IDs.

## Notes

Suggestion origin: echonomicon

Widened (the person, 2026-11-26): "we need a general renumbering system, eg for renumbering temp tickets". Sketch: `chitty renumber <ID>` (on `main`) gives any ticket, provisional or not, sharing its ID or not, the next sequential number, and rewrites references to the old ID in other tickets when the old ID names only that file (a shared ID still lists the referencing tickets to check, as today). This covers the echonomicon case above (a provisional ID with no clash) and lets a person tidy any ID by hand. Landing a plan branch renumbers its provisional tickets in TASK-340; this ticket is the single-ticket command it can reuse.

## History

- 2026-11-24T22:21:23Z zesty-coral-newt → backlog
- 2026-11-24T22:21:24Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:36Z zesty-coral-newt: changed labels
- 2026-11-26T11:11:51Z calm-ochre-quail: changed title, notes
- 2026-11-26T11:11:51Z calm-ochre-quail backlog → to-plan
