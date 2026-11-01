---
title: Show priority in `chitty list` and order by it
status: review
priority: high
created: 2026-11-01
---

## Description

Tasks already have an optional `priority` field (`low`, `medium`, `high`; `-p` on `add` and `edit`), but `chitty list` neither shows nor sorts by it, so nobody can see what matters most. Using `depends_on` for urgency would be wrong: it would mark unrelated work as queued (TASK-70). Show a priority column only when some listed task has one, sort high before medium before low before unset within each status, and include it in `--json`. `chitty next` (TASK-76) uses the same order.

## Plan

Replace the identifier tie-breaker in shared list ordering with the input sequence preserved by Python’s stable sort. Add a regression test spanning two contexts and more than nine task IDs, first confirming it fails under the string-ID sort; then verify both text and JSON list results preserve repository context and numeric task order for equal status and priority.

## Notes

Implemented shared selected-status and priority ordering for `list`; JSON already carried the model priority field and now follows that order. Verified with `make check` and `chitty fix`.

Reviewed: independent review of `28e7e25` found no findings.

Review failed (independent review by a separate session; the earlier pass was a subagent self-check by the implementing session, so it did not count): `ordered` in `store.py` breaks ties with `str(stored.id)`, a string sort. With ten tasks, `chitty list` prints `TASK-1`, `TASK-10`, `TASK-2`, ..., and `HUMAN-1` now comes before every `TASK` regardless of context order in config. Before this change, list kept `repo.tasks` order (contexts in config order, then numeric). Fix: drop the ID from the sort key and rely on `sorted` being stable, so ties keep the existing order; add a test with at least ten tasks across two contexts. The rest is good: conditional priority column, `high > medium > low > unset` within each status, JSON in the same order, PLAN.md updated.

Fixed the review finding: equal-priority items now retain the repository traversal order instead of sorting IDs lexically. Added and first ran the regression test under the unfixed ordering; it failed with `HUMAN-1` and `TASK-10` misplaced. Verified with the focused test, `make format`, and `make check`.

## Summary

Preserves context traversal and numeric ID order for equal list status/priority ties. Verified with `make check`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
- 2026-11-01 done → doing
- 2026-11-01 doing → review
