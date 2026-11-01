---
title: Show priority in `chitty list` and order by it
status: review
priority: high
created: 2026-11-01
---

## Description

Tasks already have an optional `priority` field (`low`, `medium`, `high`; `-p` on `add` and `edit`), but `chitty list` neither shows nor sorts by it, so nobody can see what matters most. Using `depends_on` for urgency would be wrong: it would mark unrelated work as queued (TASK-70). Show a priority column only when some listed task has one, sort high before medium before low before unset within each status, and include it in `--json`. `chitty next` (TASK-76) uses the same order.

## Plan

Trace list and next selection through the shared store layer. Add one priority ordering key (`high`, `medium`, `low`, unset) after status, expose the field in list JSON, and render a conditional text-table column. Add regression coverage for ordering, JSON, and the no-priority display; document the list behavior if the design specifies it.

## Notes

Implemented shared selected-status and priority ordering for `list`; JSON already carried the model priority field and now follows that order. Verified with `make check` and `chitty fix`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
