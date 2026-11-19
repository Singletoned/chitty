---
title: Stop two property tests failing at random under `make check`
status: cold-read
labels:
  - bug
priority: high
created: 2026-11-19
---

## Description

Two property tests fail at random under `make check`, and each failure has sent a runner ticket to `error` (`TASK-388` at its check before the agent started, `TASK-395` at landing, both 2026-11-18):

- `test_suffix_round_trips` in `tests/test_property_provisional.py` exceeded Hypothesis's default deadline of 200 ms per example (it took 279 ms once, then 0.06 ms). `make check` runs 16 test workers at once, so per-example timing is noise. Thirteen tests already set `deadline=None` one by one.
- `test_refused_edit_restores_repository` in `tests/test_property_refused_write.py` draws notes from `NOTES`, which can produce a setext heading underline, for example the note `0\n=`. `Repo.edit` then refuses it with `Notes text changed section boundaries; use ### for headings and close code fences`, not the `cannot finalize task write` the test expects. Reproduced on `main` 2026-11-19 by calling the test body with `("self-dependency", "0\n=", None)`.

Decisions:

- In `tests/__init__.py`, register and load a Hypothesis settings profile with `deadline=None`, so no test depends on machine load. Leave the existing per-test `deadline=None` settings alone.
- Filter `NOTES` so no line is a setext underline: a line of only `=` characters, or only `-` characters, after at most three leading spaces (trailing spaces allowed). Keep the existing filters.
- Out of scope: other flaky tests; changing how `Repo.edit` treats notes.

No property is added: both changes fix existing property tests. Their evidence is in the criteria.

## Acceptance Criteria

- [ ] A new test in `tests/test_hypothesis_profile.py` asserts `hypothesis.settings().deadline is None` when run on its own (`python -m unittest tests.test_hypothesis_profile`); it fails before the change
- [ ] `test_refused_edit_restores_repository` gains `@example(invalid="self-dependency", note="0\n=", title=None)` and `@example(invalid="cycle", note="x\n  ---", title=None)`; both fail before the `NOTES` change and pass after. Run once by hand with `max_examples=3000` (not committed), it passes; the note records that run
- [ ] `make check` passes

## History

- 2026-11-19T11:34:07Z quick-ginger-lapwing → planning
- 2026-11-19T11:34:40Z quick-ginger-lapwing planning → cold-read
