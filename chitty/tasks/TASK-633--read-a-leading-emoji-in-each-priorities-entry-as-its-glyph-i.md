---
title: Read a leading emoji in each `priorities` entry as its glyph in `chitty list`
status: planning
depends_on:
  - TASK-632
parent: TASK-607
created: 2026-11-23
---

## Description

Part of TASK-607. Decided with the person on 2026-11-23: an entry in the `priorities` list (TASK-632) may start with an emoji, which becomes that priority's glyph in `chitty list`. The default becomes `["⬆️high", "⏺️medium", "", "⬇️low"]`, which shows what `chitty list` shows today.

Parsing, in `src/chitty/config.py`: a pure function `split_priority(entry: str) -> tuple[str, str]` returns `(glyph, name)`. The glyph is the longest leading run of characters that are each in Unicode category `So` or `Sk`, or are U+FE0F (variation selector-16) or U+200D (zero-width joiner). Use `unicodedata.category`. The name is the rest, with leading whitespace removed. Examples, as probed on 2026-11-23:

- `⬆️high` (U+2B06 U+FE0F) gives `("⬆️", "high")`, and `high` gives `("", "high")`.
- `🔥 urgent` gives `("🔥", "urgent")`, `👍🏽ok` (with a skin-tone modifier, category `Sk`) gives `("👍🏽", "ok")`, and `🏳️‍🌈pride` (a ZWJ sequence) gives `("🏳️‍🌈", "pride")`.
- `-1` gives `("", "-1")`, because `-` is not a symbol of category `So`.

Validation: TASK-632's rules (`""` exactly once, no repeats, no surrounding whitespace or line break) apply to the names after splitting. An entry with a glyph but no name (`⬆️`) is refused: `priority '⬆️' has a glyph but no name`.

Ticket files, `-p`, the MCP tools, the write and `chitty check` messages, and the ordering all use names only (`priority: high`). Add `RepoConfig` properties, `priority_names` (the names, `""` kept in its place) and `priority_glyphs` (name to glyph, `""` for none), and use `priority_names` wherever TASK-632 used the raw list.

Display: `chitty list` shows `priority_glyphs[name]` in the priority column. A ticket with no priority, a name with no glyph, or an unconfigured name shows an empty column. Remove `PRIORITY_GLYPHS` from `src/chitty/model.py`, and `PRIORITIES` if nothing else uses it.

Docs: in `docs/plan/config.md`, the `priorities` line shows the new default, and one sentence says that a leading emoji is the glyph.

Tests, in a new `tests/test_priority_glyphs.py`:

- `split_priority`: each example above, and `⬆️` is refused through config validation with the message above.
- Property, with Hypothesis and `examples(50)`: for a glyph drawn from `["⬆️", "🔥", "👍🏽", "🏳️‍🌈", ""]`, a name of one or more `string.ascii_lowercase` letters, and an optional single space between them, `split_priority(glyph + space + name) == (glyph, name)`.
- `chitty list`: in a `RepoTestCase` repository with `priorities = ["🔥now", "soon", "", "later"]` inserted before the first table line of `CONFIG`, tickets `-p now` and `-p soon` are listed; the `now` line contains `🔥` and the `soon` line has no glyph. With the default config, the existing list tests in `tests/test_cli.py` pass unchanged, which shows the default reproduces today's glyphs.

Run them against `main` with TASK-632 landed, and record the failures in a note.

Out of scope: aligning glyphs that are not natively wide (TASK-576).

## Acceptance Criteria

- [ ] The `split_priority`, property and `chitty list` tests in `tests/test_priority_glyphs.py` pass, and fail before the change. Record both runs in a note
- [ ] The existing `chitty list` tests pass unchanged; `docs/plan/config.md` shows the new default; `make check` passes

## Notes

Planner, 2026-11-23: ordering moved into TASK-632 after the person decided that `priorities` is an ordered list with `""` for no priority. This ticket covers display only.

## History

- 2026-11-23T10:40:41Z witty-russet-gannet → backlog
- 2026-11-23T12:37:55Z witty-russet-gannet: changed title, description, notes
- 2026-11-23T12:54:58Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T12:54:58Z witty-russet-gannet backlog → planning
