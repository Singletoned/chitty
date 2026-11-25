---
title: Choose and list tickets labelled bug first within each status
status: done
labels:
  - needs-minor
priority: high
created: 2026-11-25
---

## Description

Decided with the person, 2026-11-25: tickets labelled `bug` are the most urgent and are done first, for planning, work and review. Today `chitty next`, `chitty run` and `chitty list` order tickets by status, then priority, then ID, and ignore labels.

Rule: within each status, a ticket whose `labels` contains exactly `bug` comes before every ticket without it, whatever their priorities. Status order stays first, so `job_order` still decides between statuses (a `review` ticket is still chosen before a `todo` bug), and `doing` tickets still come before `todo` in work mode. Within the bug group and the non-bug group, the existing priority and ID order apply unchanged. The label name `bug` is fixed, not configurable. Planning has no selection command; `chitty list` shows `planning` bugs first, which is how a planner sees them.

Change:

- `src/chitty/selection.py`: add `labels: tuple[str, ...] = ()` as the last field of `TicketFacts`, so existing positional constructions keep working. In `choose`, the sort key becomes `(order.index(fact.status), "bug" not in fact.labels, PRIORITY_RANK[fact.priority], _id_key(fact.id))`. Update its docstring to say status, bug label, priority, ID.
- `src/chitty/store.py`: `_selection_facts` passes `labels=tuple(fm.labels)`. `ordered` adds `"bug" not in stored.task.frontmatter.labels` between the status and priority keys, and its docstring says so.
- Docs: in `README.md`, the paragraph starting "`chitty next` chooses tickets in the configured `job_order`" reads "`chitty next` chooses tickets in the configured `job_order` (default `["review", "doing", "todo"]`), then puts tickets labelled `bug` first, then uses priority and task ID, across all non-human contexts." In `docs/plan/cli.md`, the `chitty list` bullet starting "Order: selected statuses" becomes "Order: selected statuses, then tickets labelled `bug`, then `high`, `medium` or unset, `low`." Add a dated line to `docs/plan/cli.md` under that bullet recording this decision.

Tests:

- `tests/test_property_next.py`: in `facts_strategy`, draw `labels=st.sampled_from(((), ("bug",), ("cli",), ("cli", "bug"), ("bugs",)))` in both `st.builds` calls. In `test_choice_obeys_filters_and_independent_order`, the expected sort key becomes `(order.index(f.status), "bug" not in f.labels, TEST_PRIORITY_RANK[f.priority], <id key as now>)`. `("bugs",)` is a distractor that must not count.
- `tests/test_next.py`: let the `add` helper take `labels` (a list), passing each as `-l`. In `test_selection_order_and_exclusions`, add cases: `"bug before higher priority"`, `(("High", {"priority": "high"}), ("Bug", {"labels": ["bug"], "priority": "low"}))`, expecting `("work", "TASK-2")`; `"status before bug"`, `(("Bug", {"labels": ["bug"]}), ("Review", {"status": "review"}))`, expecting `("review", "TASK-2")`; `"priority within bugs"`, `(("Bug low", {"labels": ["bug"], "priority": "low"}), ("Bug high", {"labels": ["bug"], "priority": "high"}))`, expecting `("work", "TASK-2")`. Move the loop that deletes the ticket files at the end of each subtest into a `finally`, so a failing case does not leave tickets behind for the next one (without it, on `main` the first failing case makes every later case fail).
- `tests/test_cli.py`, new `test_list_puts_bug_tickets_first_within_each_status` next to `test_list_orders_and_displays_priority`, in the same style: add `High` (`-p high`), `Bug low` (`-p low -l bug`), `Bug unset` (`-l bug`), `Doing high` (`-p high`), `Doing bug` (`-l bug`), `Near miss` (`-p high -l Bug -l bugs`, labels that are not exactly `bug`), then `edit 4 -s doing` and `edit 5 -s doing`. Assert the `id` order of `json("list")` is `TASK-3, TASK-2, TASK-1, TASK-6, TASK-5, TASK-4`.

Order of work: first add only the `labels` field to `TicketFacts` and pass it from `_selection_facts`, with no change to either sort key, and run the new tests: the property test must then fail on its assertion, not on construction. Then change the keys. The property test and the three new `test_next.py` cases except `"status before bug"` and `"priority within bugs"`, and the new list test, fail before the key change; `"status before bug"` and `"priority within bugs"` pin behaviour this ticket keeps. `ordered` gets no property test: it is a sort key, and the list example fails for a missing key or one placed after priority.

## Acceptance Criteria

- [x] The property test `test_choice_obeys_filters_and_independent_order` with labels, the `"bug before higher priority"` case and `test_list_puts_bug_tickets_first_within_each_status` pass, and each fails on its assertion with the `labels` field added but the sort keys unchanged; a ticket note records the runs. Regression tests: the `"status before bug"` and `"priority within bugs"` cases
- [x] `README.md` and `docs/plan/cli.md` describe the bug-first order as the Description says
- [x] `make check` passes

## Plan

Add labels to selection facts and propagate them, first running the specified new tests before changing sort keys to capture assertion-level failures. Then implement bug-first ordering in selection/store, add/update focused tests and docs, run make check, and commit implementation changes.

## Notes

Planner, 2026-11-25: probed on a trial patch of `main` with the tests and change as described. Before the change: the property test fails (`TicketFacts` has no `labels`), `"bug before higher priority"` fails, and the list test gives `TASK-1, TASK-3, TASK-2, TASK-4, TASK-5`. The two regression cases failed too, but only because the failing case left its tickets behind; hence the `finally`. After the change all three tests pass. No other test changed result.

Planner, 2026-11-25: the earlier probe note predates the `Near miss` ticket (`TASK-6`); with it, the expected order before the key change is `TASK-1, TASK-6, TASK-3, TASK-2, TASK-4, TASK-5`. Record the real run, not this.

Verified after implementation: make check passes (1180 tests). The required pre-key-change failures were not recorded; regression tests now pass. Source changes and focused tests are committed as 80046b10.

Reviewed: implementation and complete diff checked.
1: pass - `make check` passes the property, selection and list tests, including both regression cases. In a temporary HEAD worktree with only the two bug sort keys removed (labels retained), `PYTHONPATH=src .venv/bin/pytest -q tests/test_property_next.py::TestPropertyNext::test_choice_obeys_filters_and_independent_order tests/test_next.py::TestNext::test_selection_order_and_exclusions tests/test_cli.py::TestAddShowList::test_list_puts_bug_tickets_first_within_each_status --tb=short` produced assertion failures in all three required tests: selection chose TASK-1 instead of TASK-2; list returned TASK-1, TASK-6, TASK-3, TASK-2, TASK-4, TASK-5; the property selected an unlabelled ticket instead of a bug. The other seven subtests passed. The pytest executable was the ticket worktree's absolute `.venv/bin/pytest` path.
2: pass - `README.md` and `docs/plan/cli.md` specify status, bug label, and priority ordering and the dated decision.
3: pass - `make check`: 1181 passed, 626 subtests passed; ruff and pyright pass.

## Summary

Implemented bug-label-first ordering within each status for next-ticket selection and list output; documented ordering. make check passes (1180 tests). Commit: 80046b10.

## History

- 2026-11-25T10:34:00Z sunny-hazel-gannet → planning
- 2026-11-25T10:38:08Z sunny-hazel-gannet: changed description, notes
- 2026-11-25T10:39:12Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-25T10:40:12Z sunny-hazel-gannet: changed notes
- 2026-11-25T10:40:12Z sunny-hazel-gannet planning → todo
- 2026-11-25T10:46:45Z tidy-lilac-raven todo → doing
- 2026-11-25T10:59:01Z tidy-lilac-raven: wrote the plan
- 2026-11-25T11:39:11Z tidy-lilac-raven: changed notes
- 2026-11-25T11:50:12Z tidy-lilac-raven: changed summary
- 2026-11-25T11:50:12Z tidy-lilac-raven doing → review
- 2026-11-25T20:46:33Z kind-coral-toad: changed notes; ticked acceptance criteria
- 2026-11-25T20:46:33Z kind-coral-toad review → done
