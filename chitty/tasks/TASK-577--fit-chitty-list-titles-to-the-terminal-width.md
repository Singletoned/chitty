---
title: Fit chitty list titles to the terminal width
status: planning
created: 2026-11-22
---

## Description

`chitty list` cuts titles to `list_width` columns (default `LIST_WIDTH = 100`,
`src/chitty/config.py` line 24), whatever the terminal's width. In a narrower
terminal, long titles wrap onto the next line, breaking the table. Seen in
the owner's terminal (about 84 columns).

Change: in the `list` command (`src/chitty/cli.py`, around line 484, where
`room` is computed), use the smaller of `repo.config.list_width` and the
terminal width when stdout is a terminal (`sys.stdout.isatty()`), with the
width from `shutil.get_terminal_size().columns`. When stdout is not a
terminal (pipes, tests, `--json`), keep using `list_width` alone. Update the
"Titles are cut" line in `docs/plan/cli.md` (around line 55) and the
`list_width` comment in `docs/plan/config.md` (line 39) to say so.

Tests, in a new file `tests/test_list_terminal_width.py`, through
`CliTestCase` (`tests/test_cli.py`) with one ticket whose title is 90
characters:

- Patch `chitty.cli.sys.stdout.isatty` to return `True` and set the
  `COLUMNS` environment variable to `60` (`shutil.get_terminal_size` reads
  it first). Every line of `chitty list` stdout measures at most 60 columns
  by `chitty.cli._columns` and the title ends with `…`. Record that it fails
  before the change.
- Same with `COLUMNS=200` and `list_width = 100` in the default fixture:
  lines stay within 100 columns (the setting still caps).
- Without patching `isatty` (CliRunner output is not a terminal) and
  `COLUMNS=60`: the line is cut at 100 columns, not 60.

## Acceptance Criteria

- [ ] With stdout a terminal narrower than `list_width`, `chitty list` lines fit the terminal and long titles end in `…`; shown by the `COLUMNS=60` test, which fails before the change.
- [ ] `list_width` still caps a wider terminal, and non-terminal output still uses `list_width`; shown by the other two tests.
- [ ] `docs/plan/cli.md` and `docs/plan/config.md` describe the terminal cap.
- [ ] `make check` passes.

## History

- 2026-11-22T12:56:08Z friendly-jade-stoat → todo
- 2026-11-22T12:56:17Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T12:56:17Z friendly-jade-stoat todo → planning
