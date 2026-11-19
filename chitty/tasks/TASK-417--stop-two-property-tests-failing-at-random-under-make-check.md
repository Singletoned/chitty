---
title: Stop two property tests failing at random under `make check`
status: doing
labels:
  - bug
priority: high
created: 2026-11-19
---

## Description

Two property tests fail at random under `make check`, and each failure has sent a runner ticket to `error` (`TASK-388` at its check before the agent started, `TASK-395` at landing, both 2026-11-18):

- `test_suffix_round_trips` in `tests/test_property_provisional.py` exceeded Hypothesis's default deadline of 200 ms per example (it took 279 ms once, then 0.06 ms). `make check` runs the tests on all cores at once (`unittest-parallel`), so per-example timing is noise. Thirteen tests already set `deadline=None` one by one.
- `test_refused_edit_restores_repository` in `tests/test_property_refused_write.py` draws notes from `NOTES`, which can produce text that changes the ticket's section boundaries, for example the note `0\n=` (a setext heading underline). `Repo.edit` then refuses it with `Notes text changed section boundaries; use ### for headings and close code fences`, not the `cannot finalize task write` the test expects. The existing filter only rejects `#`, three backticks at column 0; `src/chitty/model.py` also treats a heading or fence after up to three leading spaces, and setext underlines, as boundaries.

Decisions:

- In `tests/__init__.py`, register and load a Hypothesis settings profile with `deadline=None`, so no test depends on machine load. Put the `hypothesis` import at the top of the file (ruff rejects a later import with E402). Leave the existing per-test `deadline=None` settings alone.
- Move the `NOTES` filter into a module-level function `plain_note(text: str) -> bool` in `tests/test_property_refused_write.py`, and filter `NOTES` with it. It returns false when the text is blank after `strip()`, or when any line, taken as `line.lstrip(" ")`, starts with `#`, three backticks, or `~~~`, or, taken as `line.lstrip(" ").rstrip(" ")`, is non-empty and made only of `=` characters or only of `-` characters. Otherwise true. Keep the `cannot finalize task write` assertion unchanged. Evidence that the old filter lets a boundary through: on `main`, `Repo.edit` with `Edit(note="0\n=", depends_on=["TASK-1"])` raises the section-boundary error.
- Out of scope: other flaky tests; changing how `Repo.edit` treats notes.

No property is added: both changes fix existing property tests, and `plain_note` is checked on a fixed list of cases, every one listed in the criteria.

## Acceptance Criteria

- [ ] The profile is registered and loaded in `tests/__init__.py` (shown by the diff), and a new test in `tests/test_hypothesis_profile.py` asserts `hypothesis.settings().deadline is None` when run on its own (`python -m unittest tests.test_hypothesis_profile`); it fails before the change on that assertion; `grep -n deadline tests/test_property_provisional.py` prints nothing
- [ ] A new `TestPlainNote` class in `tests/test_property_refused_write.py` asserts `plain_note` is false for each of `"0\n="`, `"x\n-"`, `"x\n  ---"`, `"x\n=  "`, `" # x"`, `"x\n  ## y"`, three backticks after one leading space, `"  ~~~"` and `"   "`, and true for `"plain text"`, `"a\nb = c"` and `"x - y"`. Before the change it fails because `plain_note` does not exist; the evidence that matters is the `main` reproduction in the Description, recorded in a note
- [ ] `make check` passes

## History

- 2026-11-19T11:34:07Z quick-ginger-lapwing → planning
- 2026-11-19T11:34:40Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:46:53Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:46:56Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:46:56Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T12:05:09Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T12:05:12Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T12:05:12Z quick-ginger-lapwing planning → todo
- 2026-11-19T12:05:55Z honest-coral-gannet todo → doing
