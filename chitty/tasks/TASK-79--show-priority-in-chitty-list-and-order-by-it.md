---
title: Show priority in `chitty list` and order by it
status: doing
priority: high
created: 2026-11-01
---

## Description

Tasks already have an optional `priority` field (`low`, `medium`, `high`; `-p` on `add` and `edit`), but `chitty list` neither shows nor sorts by it, so nobody can see what matters most. Using `depends_on` for urgency would be wrong: it would mark unrelated work as queued (TASK-70). Show a priority column only when some listed task has one, sort high before medium before low before unset within each status, and include it in `--json`. `chitty next` (TASK-76) uses the same order.

## Plan

Trace list and next selection through the shared store layer. Add one priority ordering key (`high`, `medium`, `low`, unset) after status, expose the field in list JSON, and render a conditional text-table column. Add regression coverage for ordering, JSON, and the no-priority display; document the list behavior if the design specifies it.

## Notes

Implemented shared selected-status and priority ordering for `list`; JSON already carried the model priority field and now follows that order. Verified with `make check` and `chitty fix`.

Reviewed: independent review of `28e7e25` found no findings.

Review failed (independent review by a separate session; the earlier pass was a subagent self-check by the implementing session, so it did not count): `ordered` in `store.py` breaks ties with `str(stored.id)`, a string sort. With ten tasks, `chitty list` prints `TASK-1`, `TASK-10`, `TASK-2`, ..., and `HUMAN-1` now comes before every `TASK` regardless of context order in config. Before this change, list kept `repo.tasks` order (contexts in config order, then numeric). Fix: drop the ID from the sort key and rely on `sorted` being stable, so ties keep the existing order; add a test with at least ten tasks across two contexts. The rest is good: conditional priority column, `high > medium > low > unset` within each status, JSON in the same order, PLAN.md updated.

## Summary

Added conditional priority display and shared priority ordering to `chitty list` text and JSON output. Verified with `make check` and `chitty fix`; review found no issues.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
- 2026-11-01 done → doing
