---
title: Prefix each note with its time and actor
status: backlog
depends_on:
  - TASK-55
created: 2026-11-01
---

## Description

Notes are append-only but undated, so a reader cannot tell when a note was written or what order events happened in across a long ticket, and a note cannot be cited from elsewhere (for example from a `blocked_by` reason). `--note` should add the timestamp itself (Chitty does the work, not the agent), giving each note a stable, merge-safe reference. Decide the format (for example a `### 2026-11-01 14:32Z` heading per note, which also delimits multi-paragraph notes) and whether it later carries the actor (TASK-57). Existing notes stay as they are.

## Notes

With the human (2026-11-01): a note's reference is its timestamp plus actor, for example `2026-11-01 14:32:05Z peach-fox`. Two branches can only collide if the same session writes two notes in the same second, and one session works one branch at a time. Chitty should still refuse a duplicate reference within a ticket when writing, and `chitty check` should report duplicates left by a merge.

## History

- 2026-11-01 → backlog
