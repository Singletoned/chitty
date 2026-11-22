---
title: Draw random property-test examples under `make test`, fixed ones under `make check`
status: cold-read
priority: high
owner: plucky-umber-wren
created: 2026-11-22
---

## Description

Today `tests/__init__.py` registers one Hypothesis profile, `tests` (`deadline=None, derandomize=True`), so every run draws the same examples (commit `11bc91db`, 2026-11-22). That suits `make check`, the quick regression check, which must give the same answer every run. It also stops property tests finding new bugs. Decided with the person, 2026-11-22: `make check` stays fixed and fast; `make test` is the thorough run that looks for new edge cases, and work and review run it (wording in a later ticket).

Change `tests/__init__.py`:

- Register two profiles. `check`: `deadline=None, derandomize=True` (today's `tests` profile, renamed; `derandomize=True` already means no example database). `thorough`: `deadline=None, derandomize=False`, with Hypothesis's default example database, so a failure found once replays on the next run in that checkout.
- Load `os.environ.get("HYPOTHESIS_PROFILE", "check")`. An unknown name must fail the import loudly; `settings.load_profile` already raises `hypothesis.errors.InvalidArgument: Profile 'nope' is not registered` (Hypothesis 6.170), so do not catch it.
- The variable must not start with `CHITTY_`: the same file deletes every `CHITTY_*`, `PI_`, `CLAUDE_` and `CODEX_` variable. Read it before that loop anyway.

Change the `Makefile` `test` target to run `HYPOTHESIS_PROFILE=thorough uv run unittest-parallel -s tests -t . --level test`, with the description `## run every test, drawing new random property-test examples`. Leave `check` as it is.

In `AGENTS.md`, replace the bullet starting `Hypothesis runs with fixed examples` with one saying `make check` uses fixed examples (profile `check`) so it repeats, and `make test` draws new random examples (profile `thorough`) to find new edge cases.

Probe for criterion 1, run with `cwd` at the repository root and the profile variable set as the case needs (removed for the unset case):

```python
import tests
from hypothesis import given, settings, strategies as st
seen = []
@settings(database=None, max_examples=20)
@given(st.integers())
def probe(x):
    seen.append(x)
probe()
print(seen)
```

`database=None` on the probe keeps it from writing the checkout's `.hypothesis/`; the database criterion reads `settings.default.database` in a separate subprocess (`import tests; from hypothesis import settings; print(settings.default.database is None)`). Two random runs of 20 integers matching by chance is negligible.

No property: a fixed set of three profile values (unset, `check`, `thorough`) plus one unknown name, each tested.

Out of scope: how many examples each profile draws (a later ticket scales per-test `max_examples`), keeping slow tests out of `make check`, and guide wording.

## Acceptance Criteria

- [ ] A new test in `tests/test_hypothesis_profiles.py` runs a probe (below) twice in subprocesses for each setting of `HYPOTHESIS_PROFILE`: unset and `check` print identical example lists across the two runs; `thorough` prints different lists; and for `thorough`, `settings.default.database` is not `None` while for unset and `check` it is `None`. Each case fails against current `main` (today the variable is ignored, so `thorough` runs repeat)
- [ ] With `HYPOTHESIS_PROFILE=nope`, `python -c "import tests"` exits non-zero with `InvalidArgument` and `nope` in stderr (tested in the same file)
- [ ] `make -n test` shows `HYPOTHESIS_PROFILE=thorough` on the `unittest-parallel` line, `make -n check` does not set `HYPOTHESIS_PROFILE`, `mate --list` lists `test` with its new description, and `make check` passes

## History

- 2026-11-22T16:27:11Z plucky-umber-wren → planning
- 2026-11-22T16:27:29Z plucky-umber-wren planning → cold-read
