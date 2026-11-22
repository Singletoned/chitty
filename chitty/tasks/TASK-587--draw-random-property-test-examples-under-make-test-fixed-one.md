---
title: Draw random property-test examples under `make test`, fixed ones under `make check`
status: doing
priority: high
created: 2026-11-22
---

## Description

Today `tests/__init__.py` registers one Hypothesis profile, `tests` (`deadline=None, derandomize=True`), so every run draws the same examples (commit `11bc91db`, 2026-11-22). That suits `make check`, the quick regression check, which must give the same answer every run. It also stops property tests finding new bugs. Decided with the person, 2026-11-22: `make check` stays fixed and fast; `make test` is the thorough run that looks for new edge cases, and work and review run it (wording in a later ticket).

Change `tests/__init__.py`:

- Register two profiles. `check`: `deadline=None, derandomize=True` (today's `tests` profile, renamed; `derandomize=True` already means no example database). `thorough`: `deadline=None, derandomize=False`, with Hypothesis's default example database, so a failure found once replays on the next run in that checkout. No `.gitignore` change: Hypothesis writes `.hypothesis/.gitignore` (`*`) itself, and `git status --ignored` already shows `.hypothesis/` as ignored.
- Load `os.environ.get("HYPOTHESIS_PROFILE", "check")`. The default is deliberate: plain `python -m unittest` and editor runs set no variable and should get the repeatable profile. An unknown name must fail the import loudly; `settings.load_profile` already raises `hypothesis.errors.InvalidArgument: Profile 'nope' is not registered` (Hypothesis 6.170), so do not catch it.
- The variable must not start with `CHITTY_`: the same file deletes every `CHITTY_*`, `PI_`, `CLAUDE_` and `CODEX_` variable. Read it before that loop anyway.

Change the `Makefile` `test` target to run `HYPOTHESIS_PROFILE=thorough uv run unittest-parallel -s tests -t . --level test`, with the description `## run every test, drawing new random property-test examples`. In `check`, change only its `unittest-parallel` line to start `HYPOTHESIS_PROFILE=check`, so a variable exported in the shell or `.envrc` cannot make `make check` random.

In `AGENTS.md`, replace the bullet starting `Hypothesis runs with fixed examples` with one saying `make check` uses fixed examples (profile `check`) so it repeats, and `make test` draws new random examples (profile `thorough`) to find new edge cases. Keep its sentence `A property test that fails is a real failure: fix it, do not rerun.`

Probe for criterion 1, run as `python -c <probe>` with `cwd` at the repository root (so `import tests` resolves) and the profile variable set as the case needs (removed for the unset case):

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

- [ ] New tests in the existing `tests/test_hypothesis_profile.py` (keep its `test_deadline_is_disabled`, which still holds) run a probe (below) twice in subprocesses for each setting of `HYPOTHESIS_PROFILE`, removing it from the child environment for the unset case and setting it explicitly otherwise (so the tests hold when `make test` exports `thorough`): unset and `check` print identical example lists across the two runs; `thorough` prints different lists; and for `thorough`, `settings.default.database` is not `None` while for unset and `check` it is `None`. The `thorough` cases fail against current `main` (today the variable is ignored, so its runs repeat); the unset and `check` cases pass there and guard against regression
- [ ] With `HYPOTHESIS_PROFILE=nope`, `python -c "import tests"` exits non-zero with `InvalidArgument` and `nope` in stderr (tested in the same file; on `main` it exits 0)
- [ ] `make -n test` shows `HYPOTHESIS_PROFILE=thorough` and `make -n check` shows `HYPOTHESIS_PROFILE=check`, each on its `unittest-parallel` line; `mate --list` (`mate` is on `PATH`) lists `test` with its new description; and `make check` passes

## History

- 2026-11-22T16:27:11Z plucky-umber-wren → planning
- 2026-11-22T16:27:29Z plucky-umber-wren planning → cold-read
- 2026-11-22T16:28:34Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T16:28:34Z plucky-umber-wren cold-read → planning
- 2026-11-22T16:28:36Z plucky-umber-wren planning → cold-read
- 2026-11-22T16:29:32Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T16:29:32Z plucky-umber-wren cold-read → planning
- 2026-11-22T16:29:33Z plucky-umber-wren planning → cold-read
- 2026-11-22T16:30:21Z plucky-umber-wren: changed description
- 2026-11-22T16:30:21Z plucky-umber-wren cold-read → planning
- 2026-11-22T16:30:23Z plucky-umber-wren: changed owner
- 2026-11-22T16:30:23Z plucky-umber-wren planning → todo
- 2026-11-22T16:31:38Z youthful-white-dormouse todo → doing
