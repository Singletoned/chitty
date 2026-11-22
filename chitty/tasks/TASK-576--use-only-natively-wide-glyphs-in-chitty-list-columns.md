---
title: Use only natively wide glyphs in chitty list columns
status: doing
labels:
  - needs-minor
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
- broken dependency (`BROKEN_DEPENDENCY_GLYPH`, `src/chitty/store.py` line
  73, plus the literal in `src/chitty/selection.py` line 102, which should
  use the constant): `⚠️` → `💔`
- running (`src/chitty/selection.py` line 83): `▶` → `🏃`

The JSON `skipped` strings change with them (`🙋 untestable`, `💔 <message>`,
`🏃 running`). Update every use in `src/`, `tests/`, `README.md`,
`docs/plan/cli.md` and `docs/plan/next-action-and-runner.md` (find them with
`grep -rn "⬆️\|⏺️\|⬇️\|✍️\|⚠️\|▶" src tests docs README.md`; known
inline uses include `tests/test_property_next.py` lines 140, 152, 161 and
166 and `tests/test_list_untestable.py` line 12). Leave `_columns` as it is.

Every glyph in a skip string in `src/chitty/selection.py` must come from a
module constant (no inline glyph literals), so the test below sees them all:
lift the human, untestable and running glyphs to constants, and make line
102 use `BROKEN_DEPENDENCY_GLYPH`. `store.py` already imports from
`chitty.selection`, so move the constant to `selection.py` and import it in
`store.py` and `cli.py`. The grep criterion is what catches an inline glyph
left behind; the test below covers the constants.

Test, in a new file `tests/test_list_glyphs.py`: collect every glyph
`chitty list` can print in its status, priority and skip columns
(`STATUS_GLYPHS` and `PRIORITY_GLYPHS` values from `chitty.model`;
`DEPENDENCY_GLYPH`, `BLOCKER_GLYPH` and the human, untestable and running
constants from `chitty.selection`; `BROKEN_DEPENDENCY_GLYPH` from wherever it
ends up). Write the test without the old glyphs as literals, so the grep
criterion stays clean. For each non-empty
glyph, assert it is one character, has no U+FE0F, and has
`unicodedata.east_asian_width` `W`. Run it before the change and record that
it fails.

Also add, in the same file, a `CliTestCase` test listing two `todo` tickets,
one with `priority: high` and one with no priority: the title starts at the
same `_columns` offset on both lines. Existing expected strings in
`tests/test_cli.py` (around lines 1199-1215) and `tests/test_run_lock.py`
(around line 143) change padding with the new glyphs; update them so columns
stay aligned.

## Acceptance Criteria

- [ ] No glyph in the `chitty list` status, priority or skip columns is a narrow character or uses U+FE0F; shown by `tests/test_list_glyphs.py`, which fails before the change.
- [ ] README and `docs/plan/` show the new glyphs; `grep -rn "⬆️\|⏺️\|⬇️\|✍️\|⚠️\|▶" src tests docs README.md` prints nothing.
- [ ] `make check` passes.
- [ ] A row with no priority and a row with `⏫` start their titles at the same column; shown by the alignment test.

## Plan

Add glyph and column-alignment regression tests, verify failure on existing behavior, replace glyphs and centralize skip constants, update expectations and documentation, then format and run checks.

## Notes

Cold read 2: constant placement fixed to `selection.py`, alignment test added; nothing else serious.

Before the fix, test_list_glyphs fails for all three priority glyphs because each contains two characters; the alignment test passes under the existing _columns calculation.

## History

- 2026-11-22T12:56:07Z friendly-jade-stoat → todo
- 2026-11-22T12:56:23Z friendly-jade-stoat: changed labels, acceptance criteria
- 2026-11-22T12:56:23Z friendly-jade-stoat todo → planning
- 2026-11-22T12:57:13Z friendly-jade-stoat: changed description
- 2026-11-22T12:58:27Z friendly-jade-stoat: changed description, acceptance criteria, notes
- 2026-11-22T12:58:27Z friendly-jade-stoat planning → todo
- 2026-11-22T15:12:53Z golden-zinc-eel todo → doing
- 2026-11-22T15:15:45Z golden-zinc-eel: wrote the plan
- 2026-11-22T15:16:06Z golden-zinc-eel: changed notes
