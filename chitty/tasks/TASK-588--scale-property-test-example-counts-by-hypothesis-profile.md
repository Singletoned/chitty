---
title: Scale property-test example counts by Hypothesis profile
status: doing
depends_on:
  - TASK-587
created: 2026-11-22
---

## Description

`TASK-587` adds two Hypothesis profiles in `tests/__init__.py`: `check` (fixed examples, for the quick `make check`) and `thorough` (random examples, for `make test`), chosen by the `TEST_TIER` variable. Both still draw the same number of examples, because 25 `@settings` decorators set `max_examples` themselves (`git grep` finds a 26th, inside the `PROBE` string in `tests/test_hypothesis_profile.py`; leave that probe as it is), which overrides any profile (counts from 5 to 300, listed by `grep -rn "max_examples" tests`). Decided with the person, 2026-11-22: `make check` should be fast and `make test` thorough; any split is arbitrary, so pick a reasonable one and watch it (a later ticket records per-test timings).

Add to `tests/__init__.py`, above the `settings.register_profile` calls (they use it):

- Module constants `CHECK_EXAMPLE_DIVISOR = 5` and `THOROUGH_EXAMPLE_FACTOR = 5`.
- A pure function `example_count(profile: str, base: int) -> int`: `max(1, base // CHECK_EXAMPLE_DIVISOR)` for `check`, `base * THOROUGH_EXAMPLE_FACTOR` for `thorough`, and `ValueError(f"no example count for Hypothesis profile {profile!r}")` otherwise.
- `examples(base: int) -> int`, returning `example_count(settings.get_current_profile_name(), base)`. `settings.get_current_profile_name()` is public in Hypothesis 6.170.
- Give the profiles `max_examples=example_count(<name>, 100)` (100 is Hypothesis's default), so tests without their own count also scale: 20 under `check`, 500 under `thorough`.

Replace every `max_examples=<value>` in a `@settings(...)` decorator under `tests/` (the new `tests/test_example_counts.py` included: its own property tests use `examples(...)` too) with `max_examples=examples(<value>)`, keeping the value (today's count becomes the base). In `tests/test_property_inbox.py`, use `examples(EXAMPLES)`. `tests/test_property_renumbering.py` defines its own module-level `examples(fn)`; it sets no `max_examples`, so leave it, and do not import `tests.examples` into it. Leave other keywords on those decorators as they are.

Out of scope, unchanged: `settings=settings(max_examples=...)` passed to `hypothesis.find` (in `tests/test_squash_bookkeeping.py`, `tests/test_ticket_strategies.py` and `tests/test_ticket_placement_reads.py`). Those search for a counterexample to a mutant and fail if they stop too early, so fewer examples would break them; they are not decorators, so criterion 2 ignores them. Also out of scope: `EXAMPLES` in `tests/test_property_renumbering.py`, which is a list of cases, not a count.

Record the wall time of `make check` and of `make test`, before and after the change, in a note: `thorough` now draws up to 1500 examples for the base-300 tests in `tests/test_property_next.py`, and the person wants to watch the split.

Property for criterion 1 over generated `base`; the profile names are a fixed set of two plus generated other text.

## Acceptance Criteria

- [ ] Property tests in `tests/test_example_counts.py`, with Hypothesis, of the pure `example_count(profile, base)` in `tests/__init__.py`: for any `base` from `st.integers(1, 100000)`, `example_count("check", base) == max(1, base // CHECK_EXAMPLE_DIVISOR)` and `example_count("thorough", base) == base * THOROUGH_EXAMPLE_FACTOR`; and for any `st.text().filter(lambda t: t not in {"check", "thorough"})` it raises `ValueError` whose message contains `repr(text)`. They fail before the change on behaviour, not import: first commit `example_count` raising `NotImplementedError`, run the tests, then implement
- [ ] A test in the same file parses every `tests/**/*.py` with `ast` and finds no `settings(...)` call used as a decorator whose `max_examples` keyword is anything but a call to `examples(...)`; on `main` it fails, listing the decorators that still use a literal or a name such as `EXAMPLES`
- [ ] A test in `tests/test_example_counts.py` runs `[sys.executable, "-c", "import tests; from hypothesis import settings; print(settings.default.max_examples, tests.examples(25))"]` with `cwd` at the repository root and `TEST_TIER` set explicitly to `check`, then to `thorough`, and asserts the output `20 5` and `500 125`; on `main` it fails (the profiles draw 100 and `examples` does not exist); and `make check` passes

## Plan

Measure baseline test timings, add and verify failing regression tests against a committed stub, implement profile scaling and decorator migration, then run checks and record timings.

## Notes

Planner, 2026-11-22: written against `TASK-587`'s planned profile names (`check`, `thorough`) and `HYPOTHESIS_PROFILE`. Keep in `planning` until `TASK-587` is `done`; then compare with what landed in `tests/__init__.py` and cold-read before `todo`.

Planner, 2026-11-22: `TASK-587` now names the variable `TEST_TIER` (was `HYPOTHESIS_PROFILE`).

Planner, 2026-11-22: compared with what `TASK-587` landed (`tests/__init__.py` registers `check` and `thorough`, loads `TEST_TIER`); this text still holds.

## History

- 2026-11-22T16:41:56Z plucky-umber-wren → planning
- 2026-11-22T16:42:04Z plucky-umber-wren: changed notes
- 2026-11-22T16:46:31Z plucky-umber-wren: changed description, acceptance criteria, notes
- 2026-11-22T17:06:23Z plucky-umber-wren: changed notes
- 2026-11-22T17:06:23Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:07:21Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T17:07:21Z plucky-umber-wren cold-read → planning
- 2026-11-22T17:07:23Z plucky-umber-wren planning → cold-read
- 2026-11-22T17:08:07Z plucky-umber-wren: changed description
- 2026-11-22T17:08:07Z plucky-umber-wren cold-read → planning
- 2026-11-22T17:08:09Z plucky-umber-wren: changed owner
- 2026-11-22T17:08:09Z plucky-umber-wren planning → todo
- 2026-11-22T17:08:29Z eager-bronze-vole todo → doing
- 2026-11-22T17:10:25Z eager-bronze-vole: wrote the plan
