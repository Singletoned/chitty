---
title: Add the `provisional` ticket field and a provisional ID suffix
status: doing
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), only `main` hands out sequential ticket numbers. A ticket created anywhere else (a follow-up found on a ticket branch, possibly in a container that cannot see other branches) gets a provisional ID that cannot clash and is visibly marked for renumbering, apart from its ID. `TASK-381` renumbers them on `main` later; that is cosmetic, so provisional IDs must work everywhere until then.

This ticket adds only the two building blocks, with no caller: the marker field and the ID suffix. `TASK-389` uses them.

Decisions:

- Pure function `provisional_suffix(draw: Callable[[int], int]) -> str` in `src/chitty/ids.py`, where `draw(n)` returns an index below `n`. Module constants `PROVISIONAL_LETTERS = "ABCDEFGHJKMNPQRSTVWXYZ"`, `PROVISIONAL_DIGITS = "23456789"` and `PROVISIONAL_LENGTH = 6`. The first character is drawn from the letters, the other five from `PROVISIONAL_LETTERS + PROVISIONAL_DIGITS` (index 0 is `A`, the last index is `9`), so it always contains a letter with no retry loop. `TaskId.parse(f"{prefix}-{suffix}").number == suffix`, a `str`, never an `int`. `ids.ID_RE` already accepts such suffixes; do not change it.
- New optional frontmatter field `provisional` in `Frontmatter` (`src/chitty/model.py`), typed `Literal[True] | None`. It is written `provisional: true`, after `moved_from`, and absent when `None`. The YAML loader (`_StringLoader`) reads every scalar as a string, and `Literal[True]` alone rejects the string `"true"`, so add a `field_validator("provisional", mode="before")` that maps exactly the string `true` to `True`, passes Python `True` through (as `with_field` supplies it), and passes every other value on unchanged, so `yes`, `on`, `True`, `false`, `1` and an empty value fail with Pydantic's value error naming `provisional`. A quoted `"true"` loads the same as `true` and is accepted. Add the key to `FIELD_ORDER` and `bool` to `FieldValue`, and give `_render_field` (and its type annotation) an explicit branch writing `true` (`render_scalar` takes only strings). `with_field("provisional", value)` accepts only `True` or `None` and raises `TaskError` for anything else, including `False`. Text `show` (`_format` in `src/chitty/cli.py`, which today prints Python `True`) prints `provisional: true`, and no line when absent. Together, so `with_field("provisional", True)` writes it and `with_field("provisional", None)` removes it. `show --json` includes `"provisional": true` or `null`, like other optional fields.
- `chitty check` does not validate the field against the ID form.
- Add its row to the table in `docs/plan/task-file.md`, and `"provisional": True` to the `sample()` fields in `tests/test_formatters.py`, so the formatter round trips cover it.

Tests: Hypothesis properties in a new `tests/test_property_provisional.py`: for `provisional_suffix`, generate `draw` from `st.randoms()` (`lambda n: rng.randrange(n)`) and prefixes matching `[A-Z]+`; for the field, generate tickets with `st.builds` over a base ticket as `tests/test_property_sections.py` does, with `provisional` `True` or absent, and check parse, render and `with_field` round trips; the `True` case is the one that must fail before the change. For the parser, generate any text `s` other than `true` with `st.text()` and write `provisional: <json.dumps(s)>`. Create both first raising `NotImplementedError`: `provisional_suffix`, and the field declared on `Frontmatter` with its before-validator raising, so the tests fail on behaviour rather than on `unknown frontmatter key`. The suffix test builds `f"{prefix}-{suffix}"` itself; `provisional_suffix` takes no prefix.

## Acceptance Criteria

- [ ] The `provisional_suffix` property passes: for generated draws and prefixes the suffix has `PROVISIONAL_LENGTH` characters, a first character from `PROVISIONAL_LETTERS`, only letters and digits from the two constants, and `TaskId.parse` gives it back as a `str`; and it uses the draws: `draw` always returning `0` gives `AAAAAA`, always returning `n - 1` gives `Z99999`; it fails against a `NotImplementedError` stub
- [ ] For generated tickets, rendering then parsing keeps `provisional` (`true` or absent), `with_field("provisional", None)` removes the line, `with_field("provisional", False)` raises `TaskError`, `Task.as_dict` has `"provisional": true` or `null`, and text `chitty show` prints `provisional: true` or no such line; the `True` case fails before the change
- [ ] Parser property: for any generated text other than `true`, a ticket file with `provisional: <json.dumps(text)>` fails with `TaskError` naming `provisional` and never with `unknown frontmatter key` or another exception; the examples `yes`, `on`, `True`, `false` and `1` are among those tested; `provisional: true` parses
- [ ] `tests/test_formatters.py` round trips a `sample()` ticket with `"provisional": True` through prettier and mdformat (today `sample()` raises `TaskError` for it); `docs/plan/task-file.md` has a `provisional` row giving type `true`, not required, and that it marks a provisional ID for renumbering; `make check` passes

## History

- 2026-11-18T16:20:07Z lively-quartz-crane → backlog
- 2026-11-18T16:22:50Z lively-quartz-crane: changed labels, description, acceptance criteria
- 2026-11-18T16:22:50Z lively-quartz-crane backlog → planning
- 2026-11-18T16:23:29Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:27:46Z lively-quartz-crane: changed title, labels, description, acceptance criteria
- 2026-11-18T16:27:46Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:27:48Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:29:21Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:31:16Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:31:16Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:31:31Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:33:05Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:33:05Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:33:07Z lively-quartz-crane planning → todo
- 2026-11-18T20:06:44Z honest-pearl-wren todo → doing
