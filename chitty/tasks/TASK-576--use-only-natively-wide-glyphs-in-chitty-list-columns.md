---
title: Use only natively wide glyphs in chitty list columns
status: todo
created: 2026-11-22
---

## Description

`chitty list` columns go out of line in some terminals. Seen in the owner's
terminal in another project (Echonomicon): rows with a blank priority showed
their skip marker and title one column further right than rows with `⬆️` or
`⏺️`.

Cause: `⬆️`, `⏺️`, `⬇️`, `✍️` and `⚠️` are narrow characters (East Asian
Width `N`) followed by U+FE0F. `_columns` in `src/chitty/cli.py` (around
line 490) counts U+FE0F as one extra column, so the code pads them as two
columns, but many terminals draw them as one. `▶` (width `A`) is ambiguous
too. Natively wide emoji (width `W`, such as `👤`, `🔗`, `🚧`) line up
everywhere.

Change: use only characters with East Asian Width `W` and no U+FE0F in
`chitty list` columns and in the `skipped` strings:

- priority (`PRIORITY_GLYPHS`, `src/chitty/model.py` line 69): `⬆️` → `⏫`,
  `⏺️` → `➖`, `⬇️` → `⏬`
- untestable (`src/chitty/selection.py`, around line 88): `✍️` → `🙋`
- broken dependency (`BROKEN_DEPENDENCY_GLYPH`, `src/chitty/selection.py`):
  `⚠️` → `💔`
- running (`src/chitty/selection.py` line 83): `▶` → `🏃`

The JSON `skipped` strings change with them (`🙋 untestable`, `💔 <message>`,
`🏃 running`). Update every use in `src/`, `tests/`, `README.md`,
`docs/plan/cli.md` and `docs/plan/next-action-and-runner.md` (find them with
`grep -rn "⬆️\|⏺️\|⬇️\|✍️\|⚠️\|▶" src tests docs README.md`). Leave
`_columns` as it is.

Test, in a new file `tests/test_list_glyphs.py`: collect every glyph
`chitty list` can print in its status, priority and skip columns
(`STATUS_GLYPHS` and `PRIORITY_GLYPHS` values from `chitty.model`;
`DEPENDENCY_GLYPH`, `BLOCKER_GLYPH`, `BROKEN_DEPENDENCY_GLYPH` and the
human, untestable and running glyphs from `chitty.selection`; lift the
last three to module constants if they are inline). For each non-empty
glyph, assert it is one character, has no U+FE0F, and has
`unicodedata.east_asian_width` `W`. Run it before the change and record that
it fails.

## History

- 2026-11-22T12:56:07Z friendly-jade-stoat → todo
