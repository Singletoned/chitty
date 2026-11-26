---
title: Order tickets by the configured `priorities` list
status: doing
labels:
  - needs-minor
depends_on:
  - TASK-632
parent: TASK-607
created: 2026-11-26
---

## Description

Part of TASK-607. TASK-632 adds `RepoConfig.priorities` (`src/chitty/config.py`), highest first, with `""` placing tickets that have no priority, and default `["high", "medium", "", "low"]`. This ticket orders tickets by that list. The model still allows only the built-in names; custom names are TASK-10039.

Code:

- Replace `PRIORITY_RANK` (`src/chitty/selection.py`) and `PRIORITY_ORDER` (`src/chitty/store.py`) with one pure function in `selection.py`, `priority_rank(priority: str | None, priorities: Sequence[str]) -> int`. It returns the name's index in the list, the index of `""` for `None`, and `len(priorities)` for a name not in the list.
- `choose` (`selection.py`) and `ordered` (`store.py`) take a required keyword argument `priorities` and use `priority_rank` in place of the old dicts, keeping the `"bug" not in labels` key before it. Callers pass `repo.config.priorities`: `next_action` in `store.py` and the one `ordered(...)` call in `src/chitty/cli.py`.

With the default list, one thing changes: today an unset priority ties with `medium`, and now `medium` comes first. Update the existing tests that pin the old order: in `tests/test_next.py`, the case "unset priority ties medium and uses identifier" now expects `("work", "TASK-2")`; in `tests/test_cli.py`, `test_list_orders_and_displays_priority` now expects High, Medium, Unset, Low; in `tests/test_property_next.py`, `TEST_PRIORITY_RANK` and every `choose(...)` call, which now passes `priorities=`.

Docs: the priority bullet in `docs/plan/next-action-and-runner.md` (today `high, then medium or unset, then low`) describes the configured list.

Tests, added to `tests/test_priorities_config.py` (created by TASK-632):

- Through the CLI, with the default config: tickets added with `-p low`, no priority, `-p medium` and `-p high` list (`chitty list --json`) as high, medium, none, low. This fails on `main` with TASK-632 landed, where none comes before medium.
- Property, with Hypothesis and `examples(50)`: the list is a drawn permutation of `["high", "medium", "low", ""]`, plus one to eight tickets sharing one status (from `todo`, `doing`, `review`) with priorities drawn from the built-in names or none. The test computes each expected rank itself, without calling `priority_rank`. `ordered` (with `statuses=(status,)`, no bug labels) returns a permutation of the input, sorted stably by expected rank. `choose` returns a ticket of minimal expected rank. For any name and any list with one `""`, `priority_rank` equals the expected rank, including `len(list)` for a name not in it.

Out of scope: custom priority names and their display (TASK-10039), and write validation (TASK-10038).

## Acceptance Criteria

- [ ] The default-config ordering test and the property in `tests/test_priorities_config.py` pass; the ordering test fails before the change (record it in a note); the three existing tests named in the Description are updated
- [ ] `docs/plan/next-action-and-runner.md` describes the configured order; `make check` passes

## Plan

Add a CLI regression test and verify it fails; implement shared configurable ranking for list and selection, add independent permutation properties, update existing expectations and documentation, then format and run checks.

## Notes

Before the fix, the default CLI ordering regression failed: actual high, unset, medium, low; expected high, medium, unset, low.

## History

- 2026-11-26T11:40:35Z brisk-bronze-adder → planning
- 2026-11-26T11:41:17Z brisk-bronze-adder: changed description
- 2026-11-26T11:42:42Z brisk-bronze-adder planning → cold-read
- 2026-11-26T11:45:41Z brisk-bronze-adder cold-read → planning
- 2026-11-26T11:45:48Z brisk-bronze-adder: changed title, labels, description, acceptance criteria
- 2026-11-26T11:45:48Z brisk-bronze-adder planning → todo
- 2026-11-26T14:07:07Z witty-white-kestrel todo → doing
- 2026-11-26T14:11:14Z witty-white-kestrel: wrote the plan
- 2026-11-26T14:11:56Z witty-white-kestrel: changed notes
