---
title: Accept any configured priority name in ticket frontmatter
status: review
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

Docs: the `priority` row in `docs/plan/task-file.md` (today `low|medium|high`) says any non-empty name, with configured names checked on write and by `chitty check` (TASK-10038). The MCP `Priority` type (`src/chitty/mcp.py`) is also TASK-10038; leave it.

Tests, added to `tests/test_priorities_config.py`, with `RepoTestCase` and a custom config: `CONFIG` from `tests/support.py` with `priorities = ["now", "soon", "", "later"]` inserted before its first `[` table line.

- A hand-written ticket with `priority: ""` makes `chitty.model.parse` raise `TaskError` whose message contains the text above (pydantic prefixes it).
- Hand-written tickets with `later`, no priority, `soon`, `now` and `high` list (`chitty list --json`) as now, soon, none, later, high. In `chitty list`, the `now` line contains none of `⏫`, `➖`, `⏬`, and the `high` line shows `⏫`. `chitty next --mode work` picks a `now` ticket over an older `soon` one.

Record the before-change failures once TASK-632 and TASK-10037 are on `main`: `now` does not parse there. TASK-10037 must land first, because it removes the dict lookups that would raise `KeyError` on a custom name.

Out of scope: write and check validation (TASK-10038), and how custom names display (TASK-633).

## Acceptance Criteria

- [ ] The `priority: ""` and custom-name list and next tests in `tests/test_priorities_config.py` pass and fail before the change (record the failures in a note)
- [ ] The `task-file.md` priority row is updated; `make check` passes

## Plan

Add hand-written frontmatter and CLI ordering regression tests and record their failures; allow non-empty priority strings, safely render unknown glyphs, update the task-file specification, then format and run checks.

## Notes

Before the fix, pytest CustomPriorityTests failed both tests: empty priority reported the built-in literal choices instead of the required message, and list rejected the custom priority soon as not one of those choices.

## Summary

Frontmatter accepts non-empty priority names; list displays unknown names without a glyph. Added custom ordering, next, display and empty-value tests; make check passes.

## History

- 2026-11-26T11:45:33Z brisk-bronze-adder → planning
- 2026-11-26T11:46:52Z brisk-bronze-adder planning → cold-read
- 2026-11-26T11:47:55Z brisk-bronze-adder cold-read → planning
- 2026-11-26T11:48:00Z brisk-bronze-adder: changed description
- 2026-11-26T11:48:00Z brisk-bronze-adder planning → todo
- 2026-11-26T14:35:35Z plucky-maroon-urchin todo → doing
- 2026-11-26T14:39:44Z plucky-maroon-urchin: wrote the plan
- 2026-11-26T14:40:32Z plucky-maroon-urchin: changed notes
- 2026-11-26T14:44:33Z plucky-maroon-urchin: changed summary
- 2026-11-26T14:47:07Z plucky-maroon-urchin doing → review
