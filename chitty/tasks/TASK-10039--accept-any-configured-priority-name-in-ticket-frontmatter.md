---
title: Accept any configured priority name in ticket frontmatter
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-10037
parent: TASK-607
created: 2026-11-26
---

## Description

Part of TASK-607. TASK-632 adds `RepoConfig.priorities`, and TASK-10037 orders tickets by it through `priority_rank` (`src/chitty/selection.py`). Today `Frontmatter.priority` in `src/chitty/model.py` is `Literal["low", "medium", "high"] | None`, so a custom name such as `now` cannot be stored. This ticket lets the model hold any non-empty name. Write validation is TASK-10038; until it lands, `chitty add -p` and `chitty edit -p` still accept only the built-in names, and custom names come only from hand-written files.

Code:

- `Frontmatter.priority` becomes `str | None` and refuses `""` with `priority must not be empty; remove the key instead`. `PRIORITIES` stays, as the built-in names.
- `chitty list` (`src/chitty/cli.py`, `_two_columns(PRIORITY_GLYPHS[fm.priority])`) becomes `PRIORITY_GLYPHS.get(fm.priority, "")`. This has to land with the model change, or `chitty list` raises `KeyError` on a custom name.

Docs: the `priority` row in `docs/plan/task-file.md` (today `low|medium|high`) says any configured name.

Tests, added to `tests/test_priorities_config.py`, with `RepoTestCase` and a custom config: `CONFIG` from `tests/support.py` with `priorities = ["now", "soon", "", "later"]` inserted before its first `[` table line.

- A hand-written ticket with `priority: ""` makes `chitty.model.parse` raise with the message above.
- Hand-written tickets with `later`, no priority, `soon`, `now` and `high` list (`chitty list --json`) as now, soon, none, later, high. In `chitty list`, the `now` line contains none of `⏫`, `➖`, `⏬`, and the `high` line shows `⏫`. `chitty next --mode work` picks a `now` ticket over an older `soon` one.

Both fail on `main` with TASK-10037 landed, because `now` does not parse.

Out of scope: write and check validation (TASK-10038), and how custom names display (TASK-633).

## Acceptance Criteria

- [ ] The `priority: ""` and custom-name list and next tests in `tests/test_priorities_config.py` pass and fail before the change (record the failures in a note)
- [ ] The `task-file.md` priority row is updated; `make check` passes

## History

- 2026-11-26T11:45:33Z brisk-bronze-adder → planning
