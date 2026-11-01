---
title: Prefix each note with its date and time
status: backlog
created: 2026-11-01
---

## Description

Notes are append-only but undated, so a reader cannot tell when a note was written or what order events happened in across a long ticket, and a note cannot be cited from elsewhere (for example from a `blocked_by` reason). `--note` should add the timestamp itself (Chitty does the work, not the agent), giving each note a stable, merge-safe reference. Decide the format (for example a `### 2026-11-01 14:32Z` heading per note, which also delimits multi-paragraph notes) and whether it later carries the actor (TASK-57). Existing notes stay as they are.

## History

- 2026-11-01 → backlog
