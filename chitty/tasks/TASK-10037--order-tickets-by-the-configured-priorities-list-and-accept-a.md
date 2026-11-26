---
title: Order tickets by the configured `priorities` list and accept any priority name in the model
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-632
parent: TASK-607
created: 2026-11-26
---

## Description

Part of TASK-607. TASK-632 adds the `priorities` setting to `RepoConfig` (`src/chitty/config.py`), highest first, with `""` placing tickets that have no priority, and default `["high", "medium", "", "low"]`. This ticket makes the model accept any priority name and orders tickets by the configured list. Write and check validation is TASK-10038; until it lands, `chitty add -p` and `chitty edit -p` still accept only the built-in names.

Model (`src/chitty/model.py`): `Frontmatter.priority` becomes `str | None` and refuses an empty string with `priority must not be empty; remove the key instead`. `PRIORITIES` stays, as the built-in names.

Ordering: replace `PRIORITY_RANK` (`src/chitty/selection.py`) and `PRIORITY_ORDER` (`src/chitty/store.py`) with one pure function in `src/chitty/selection.py`, `priority_rank(priority: str | None, priorities: Sequence[str]) -> int`. It returns the index of the name in the list, with `None` at the index of `""`, and `len(priorities)` for a name that is not in the list. `choose` (`selection.py`) and `ordered` (`store.py`) take a required keyword argument `priorities` and use `priority_rank` in place of the old dicts, keeping the `"bug" not in labels` key before it. Their callers pass `repo.config.priorities`: `next_action` in `store.py` and the `ordered(...)` call in `src/chitty/cli.py`.

With the default list, this changes one thing: today an unset priority ties with `medium`; now `medium` comes first.

Display: `chitty list` uses `PRIORITY_GLYPHS.get(priority, "")`, so a name with no built-in glyph shows an empty priority column (TASK-633 decides more).

Docs: update the `priority` row in `docs/plan/task-file.md` (today `low|medium|high`) and the priority bullet in `docs/plan/next-action-and-runner.md` (today `high, then medium or unset, then low`) to describe the configured list.

Existing tests that pin the old order must change. List each in a note: `tests/test_next.py` ("unset priority ties medium", which now expects the `medium` ticket first), `tests/test_property_next.py` (`TEST_PRIORITY_RANK`, and every `choose(...)` call, which now passes `priorities=`), and `test_list_orders_and_displays_priority` in `tests/test_cli.py`.

Tests, in `tests/test_priorities_config.py` (created by TASK-632), with `RepoTestCase`. The custom config is `CONFIG` from `tests/support.py` with `priorities = ["now", "soon", "", "later"]` inserted before its first `[` table line:

- Model: a hand-written ticket with `priority: ""` makes `chitty.model.parse` raise with the message above.
- Ordering, through the CLI: with the default config, tickets added with `-p low`, no priority, `-p medium` and `-p high` list (`chitty list --json`) as high, medium, none, low. With the custom config, hand-written tickets with `later`, no priority, `soon`, `now` and `high` list as now, soon, none, later, high, and `chitty list` prints the `now` line without `⬆️`, `⏺️` or `⬇️`, while the `high` line still shows `⬆️`. `chitty next --mode work` picks a `now` ticket over an older `soon` one.
- Property, with Hypothesis and `examples(50)`: draw two to five distinct lowercase names with `""` inserted at a drawn position, and one to eight tickets sharing one status (from `todo`, `doing`, `review`), each with a priority drawn from the list (`""` meaning none) or one name outside it. The test computes each expected rank itself, without calling `priority_rank`. `ordered` (given `statuses=(status,)`) returns a permutation of the input sorted stably by expected rank (with bug labels absent); `choose` returns a ticket of minimal expected rank; and `priority_rank` equals the expected rank for every drawn priority.

Each new test except the property fails on `main`: there, custom names do not parse, and no priority ties `medium`.

Out of scope: refusing unconfigured names on write or in `chitty check`, CLI and MCP option types (TASK-10038), and how custom names display (TASK-633).

## Acceptance Criteria

- [ ] The model, ordering and display tests in `tests/test_priorities_config.py` pass and fail on `main`; the property passes; changed existing tests are listed in a note
- [ ] The two plan docs describe the configured order; `make check` passes

## History

- 2026-11-26T11:40:35Z brisk-bronze-adder → planning
- 2026-11-26T11:41:17Z brisk-bronze-adder: changed description
