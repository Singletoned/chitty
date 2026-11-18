---
title: Add the `provisional` ticket field and a provisional ID suffix
status: planning
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), only `main` hands out sequential ticket numbers. A ticket created anywhere else (a follow-up found on a ticket branch, possibly in a container that cannot see other branches) gets a provisional ID that cannot clash and is visibly marked for renumbering, apart from its ID. `TASK-381` renumbers them on `main` later; that is cosmetic, so provisional IDs must work everywhere until then.

This ticket adds only the two building blocks, with no caller: the marker field and the ID suffix. `TASK-389` uses them.

Decisions:

- Pure function `provisional_suffix(draw: Callable[[int], int]) -> str` in `src/chitty/ids.py`, where `draw(n)` returns an index below `n`. Module constants `PROVISIONAL_LETTERS = "ABCDEFGHJKMNPQRSTVWXYZ"`, `PROVISIONAL_DIGITS = "23456789"` and `PROVISIONAL_LENGTH = 6`. The first character is drawn from the letters, the other five from letters plus digits, so it always contains a letter with no retry loop. `TaskId.parse(f"{prefix}-{suffix}").number == suffix`, a `str`, never an `int`. `ids.ID_RE` already accepts such suffixes; do not change it.
- New optional frontmatter field `provisional` in `Frontmatter` (`src/chitty/model.py`), typed `Literal[True] | None`. It is written `provisional: true`, after `moved_from`, and absent when `None`. Only the text `true` is accepted: the YAML loader reads every scalar as a string, so any other value (`yes`, `on`, `True`, `false`) is a parse error naming the field. Add it to `FIELD_ORDER`, `FieldValue` and `_render_field`, so `with_field("provisional", True)` writes it and `with_field("provisional", None)` removes it. `show --json` includes `"provisional": true` or `null`, like other optional fields.
- `chitty check` does not validate the field against the ID form.
- Add its row to the table in `docs/plan/task-file.md`, and `"provisional": True` to the `sample()` fields in `tests/test_formatters.py`, so the formatter round trips cover it.

Tests: Hypothesis properties in a new `tests/test_property_provisional.py`: for `provisional_suffix`, generate `draw` from `st.randoms()` (`lambda n: rng.randrange(n)`) and prefixes matching `[A-Z]+`; for the field, generate tickets with and without it and check parse, render and `with_field` round trips. Create both names first raising `NotImplementedError` (the field as a stub validator), so the tests fail on behaviour.

## Acceptance Criteria

- [ ] The `provisional_suffix` property passes: for generated draws and prefixes the suffix has `PROVISIONAL_LENGTH` characters, a first character from `PROVISIONAL_LETTERS`, only letters and digits from the two constants, and `TaskId.parse` gives it back as a `str`; it fails against a `NotImplementedError` stub
- [ ] For generated tickets, rendering then parsing keeps `provisional` (`true` or absent), `with_field("provisional", None)` removes the line, and a ticket file with `provisional: yes`, `on`, `True` or `false` fails to parse with an error naming `provisional`; the test fails before the change
- [ ] `tests/test_formatters.py` round trips a ticket with `provisional: true` through prettier and mdformat; `docs/plan/task-file.md` lists the field; `make check` passes

## History

- 2026-11-18T16:20:07Z lively-quartz-crane → backlog
- 2026-11-18T16:22:50Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T16:22:50Z lively-quartz-crane backlog → planning
- 2026-11-18T16:23:29Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:27:46Z lively-quartz-crane: changed title, labels, description, acceptance criteria
- 2026-11-18T16:27:46Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:27:48Z lively-quartz-crane: changed acceptance criteria
