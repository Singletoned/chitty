---
title: Show `due` in `chitty list` and filter with `--due-before`
status: backlog
depends_on:
  - TASK-628
parent: TASK-619
created: 2026-11-23
---

## Description

`chitty list` shows a ticket's due date compactly and marks overdue ones (due before today). `chitty list --due-before DATE` keeps only tickets with a due date before DATE. `--json` includes `due`. Decide while planning whether default sorting changes; if it does, say how it combines with priority.

## History

- 2026-11-23T10:39:48Z witty-russet-gannet → backlog
- 2026-11-23T10:39:59Z witty-russet-gannet: changed dependencies
