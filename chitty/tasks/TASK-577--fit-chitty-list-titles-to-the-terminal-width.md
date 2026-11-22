---
title: Fit chitty list titles to the terminal width
status: done
created: 2026-11-22
---

## Description

`chitty list` cuts titles to `list_width` columns (default `LIST_WIDTH = 100`,
`src/chitty/config.py` line 24), whatever the terminal's width. In a narrower
terminal, long titles wrap onto the next line, breaking the table. Seen in
the owner's terminal (about 84 columns).

Change, in `src/chitty/cli.py`:

- Add `_terminal_columns() -> int | None`: `None` when `sys.stdout.isatty()`
  is false, otherwise `shutil.get_terminal_size().columns`. This is the seam
  tests patch: `CliRunner` replaces `sys.stdout`, so patching `isatty` from a
  test does not reach the command.
- Add pure `_list_width(setting: int, terminal: int | None) -> int`:
  `setting` when `terminal` is `None`, else `min(setting, terminal)`.
- In the `list` command, where `room` is computed (around line 484), use
  `_list_width(repo.config.list_width, _terminal_columns())` in place of
  `repo.config.list_width`.

Accepted limits, unchanged by this ticket: labels stay whole, so long labels
may still overflow; and when the terminal is narrower than the id, status,
priority and marker columns, `room` drops to zero or below, the title becomes
`…` and the line may overflow.

Update the "Titles are cut" line in `docs/plan/cli.md` (around line 55) and
the `list_width` comment in `docs/plan/config.md` (line 39): titles fit the
smaller of `list_width` and the terminal width when stdout is a terminal.

Tests, in a new file `tests/test_list_terminal_width.py`:

- `_list_width(100, None) == 100`, `_list_width(100, 60) == 60`,
  `_list_width(100, 200) == 100`.
- Through `CliTestCase` (`tests/test_cli.py`) with one ticket whose title is
  90 characters and no labels or priority, patching
  `chitty.cli._terminal_columns` to return `60`: the ticket's line in
  `chitty list` stdout measures at most 60 columns by `chitty.cli._columns`
  and ends with `…`. Patch with `create=True`; record that before the
  change it fails on the at-most-60 assertion (the line measures 100).
- The unpatched 100-column cut is already covered by
  `test_list_width_defaults_to_one_hundred_columns` (`tests/test_cli.py`
  line 1143); it must still pass. Add no duplicate.

## Acceptance Criteria

- [x] With a terminal narrower than `list_width`, `chitty list` lines fit the terminal and long titles end in `…`; shown by the patched `_terminal_columns` test, which fails before the change.
- [x] `_list_width` returns the setting with no terminal and the smaller width otherwise; shown by the helper tests. `test_list_width_defaults_to_one_hundred_columns` still passes.
- [x] `docs/plan/cli.md` (around line 55) and `docs/plan/config.md` (line 39) each say titles fit the smaller of `list_width` and the terminal width when stdout is a terminal.
- [x] `make check` passes.

## Plan

Add a fail-first CLI width regression, implement terminal-aware width helpers, update plan documentation, and run the full checks.

## Notes

Cold read 3: wording only (fail-first assertion, reuse of the existing 100-column test, exact doc content).

Fail-first regression: python -m unittest tests.test_list_terminal_width fails the width assertion with 100 columns versus 60.

Reviewed:
1: pass - tests.test_list_terminal_width passes; replacing the list callback with main's version produces AssertionError: 100 not less than or equal to 60.
2: pass - tests.test_list_terminal_width helper test passes; tests.test_cli.TestAddShowList.test_list_width_defaults_to_one_hundred_columns prints OK.
3: pass - inspected both plan documents; each describes the smaller terminal and configured width for terminal stdout.
4: pass - make check prints 1128 tests OK, with ruff and pyright passing.

## Summary

Implemented terminal-aware list width and documentation. Regression failed before the fix at 100 versus 60 columns; make check passes.

## History

- 2026-11-22T12:56:08Z friendly-jade-stoat → todo
- 2026-11-22T12:56:17Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T12:56:17Z friendly-jade-stoat todo → planning
- 2026-11-22T12:57:28Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T12:58:17Z friendly-jade-stoat: changed description, acceptance criteria, notes
- 2026-11-22T12:58:17Z friendly-jade-stoat planning → todo
- 2026-11-22T15:24:42Z jolly-pearl-puffin todo → doing
- 2026-11-22T15:27:32Z jolly-pearl-puffin: wrote the plan
- 2026-11-22T15:27:42Z jolly-pearl-puffin: changed notes
- 2026-11-22T15:32:22Z jolly-pearl-puffin: changed summary
- 2026-11-22T15:32:22Z jolly-pearl-puffin doing → review
- 2026-11-22T15:38:07Z friendly-maroon-newt: changed notes; ticked acceptance criteria
- 2026-11-22T15:38:07Z friendly-maroon-newt review → done
