---
title: Show priority in `chitty list` and order by it
status: backlog
priority: high
created: 2026-11-01
---

## Description

Tasks already have an optional `priority` field (`low`, `medium`, `high`; `-p` on `add` and `edit`), but `chitty list` neither shows nor sorts by it, so nobody can see what matters most. Using `depends_on` for urgency would be wrong: it would mark unrelated work as queued (TASK-70). Show a priority column only when some listed task has one, sort high before medium before low before unset within each status, and include it in `--json`. `chitty next` (TASK-76) uses the same order.

## History

- 2026-11-01 → backlog
