---
title: Use only natively wide glyphs in chitty list columns
status: review
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
166 and `tests/test_list_untestable.py` line 12). Leave `_columns` as it is. (Line numbers are from `main` before this branch; find code by name.)

Status on 2026-11-23: the branch already swaps the glyphs and updates docs and expectations. Two pieces remain: `skip_reason` in `src/chitty/selection.py` still returns the literal `"👤 human"` for human context or owner, which must become `return f"{HUMAN_GLYPH} human"` (criterion 2's grep is the check for it); and the alignment test in `tests/test_list_glyphs.py` still measures with `_columns`, which must be replaced as described below.

Every glyph in a skip string in `src/chitty/selection.py` must come from a
module constant (no inline glyph literals), so the test below sees them all:
lift the human glyph (both returns, including `👤 human` for human context or owner), the untestable and the running glyphs to constants, and make line
102 use `BROKEN_DEPENDENCY_GLYPH`. `store.py` already imports from
`chitty.selection`, so move the constant to `selection.py` and import it in
`cli.py` (on this branch `store.py` no longer uses it, so it needs no import). The grep criterion is what catches an inline glyph
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
same column on both lines, measured as the failing terminals draw text. Do
not measure with `_columns`, which already counts `⬆️` as two columns and so
passes before the change. The test defines its own width function:
`unicodedata.east_asian_width` `W` or `F` counts 2, U+FE0F and combining
characters count 0, anything else counts 1. Under it the old `high` glyph is
one column narrower than its padding, so the titles differ by one column
before the change and match after it. Run it before the change and record
that it fails. Existing expected strings in
`tests/test_cli.py` (around lines 1199-1215) and `tests/test_run_lock.py`
(around line 143) change padding with the new glyphs; update them so columns
stay aligned.

## Acceptance Criteria

- [ ] No glyph in the `chitty list` status, priority or skip columns is a narrow character or uses U+FE0F; shown by `tests/test_list_glyphs.py`, which fails before the change.
- [ ] README and `docs/plan/` show the new glyphs; `grep -rn "⬆️\|⏺️\|⬇️\|✍️\|⚠️\|▶" src tests docs README.md` prints nothing, and `grep -n "\"👤 human" src/chitty/selection.py` prints nothing.
- [ ] `make check` passes.
- [ ] A row with no priority and a row with `⏫` start their titles at the same column, measured with the width rule in the Description (East Asian Width `W` or `F` counts 2, U+FE0F and combining characters 0, anything else 1), not `_columns`; shown by the alignment test, which fails before the change (titles at columns 21 and 22 on `main`).

## Plan

Replace the alignment test's _columns oracle with the specified terminal-width function and fixture; verify both regression tests fail on the old glyphs, retain the existing centralized constants, then run make check and commit implementation changes.

## Notes

Cold read 2: constant placement fixed to `selection.py`, alignment test added; nothing else serious.

Before the fix, test_list_glyphs fails for all three priority glyphs because each contains two characters; the alignment test passes under the existing _columns calculation.

Review failed (design): The alignment regression uses the unchanged `_columns` calculation, which already reports the old priority glyph as two columns. The worker's before-fix note confirms the alignment test passes before the change, so it cannot detect the reported terminal-rendering defect. Specify a verifiable regression fixture and assertions that distinguish the original behavior without relying on the unchanged calculation. Newly discovered: the human skip path also retains an inline glyph, contrary to the requirement to centralize every skip glyph; replace it with `HUMAN_GLYPH` so the glyph test covers the actual value.
1: fail - `selection.py` returns an inline human glyph for human context or owner, bypassing `HUMAN_GLYPH` and the constants test. Use the constant in that branch.
2: pass - old-glyph grep printed nothing; README and both plan documents show the replacements.
3: pass - `make check` exited 0.
4: fail - `python -m unittest tests.test_list_glyphs -v` printed OK for both tests, but the worker's before-fix note records that the alignment test also passed before the fix; its `_columns` oracle cannot demonstrate the terminal width defect. Planning must specify a discriminating test.

## Summary

Replaced the alignment-test oracle with the specified terminal width calculation in tests/test_list_glyphs.py. make check passes (1128 tests); focused glyph tests pass. Commit: c37bd797.

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
- 2026-11-22T15:21:20Z golden-zinc-eel: changed summary
- 2026-11-22T15:23:05Z golden-zinc-eel doing → review
- 2026-11-22T15:31:22Z upbeat-silver-marten: changed owner, acceptance criteria, notes
- 2026-11-22T15:31:22Z upbeat-silver-marten review → planning
- 2026-11-23T23:06:32Z mellow-amber-toad: changed description, acceptance criteria
- 2026-11-23T23:06:32Z mellow-amber-toad planning → cold-read
- 2026-11-23T23:09:13Z mellow-amber-toad: changed description, acceptance criteria
- 2026-11-23T23:09:13Z mellow-amber-toad cold-read → planning
- 2026-11-23T23:09:34Z mellow-amber-toad: changed acceptance criteria
- 2026-11-23T23:10:44Z mellow-amber-toad: changed description
- 2026-11-23T23:10:44Z mellow-amber-toad planning → todo
- 2026-11-23T23:29:30Z honest-indigo-toad todo → doing
- 2026-11-23T23:31:31Z honest-indigo-toad: wrote the plan
- 2026-11-23T23:35:36Z honest-indigo-toad: changed summary
- 2026-11-23T23:35:36Z honest-indigo-toad doing → review
