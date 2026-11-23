---
title: Show possible duplicate tickets for each suggestion in `chitty inbox`
status: backlog
parent: TASK-635
created: 2026-11-23
---

## Description

For each waiting suggestion, `chitty inbox` (and `--json`) lists existing tickets, including `done` and archived ones, whose titles are similar, so a triager sees likely duplicates without searching. Use a deterministic, explainable similarity in a pure function (for example shared significant words after lower-casing and dropping stop words, above a threshold kept as a module constant), with property tests. `--pull` prints the same hints next to each new ID. No new options.

## History

- 2026-11-23T10:41:19Z witty-russet-gannet → backlog
