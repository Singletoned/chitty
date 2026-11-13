---
title: Specify property tests by default when planning, and look for missed ones in cold reads
status: doing
created: 2026-11-12
---

## Description

- Workers test what criteria name, and criteria mostly test by example. In a random sample of 15 recent tickets, 11 could have had a property test and one did. TASK-289 said every Chitty error after the config loads is reported but tested one error, so argument errors went unreported. TASK-266 said every directory under `chitty/` but no test varied which branch a directory was on, so directories only on another branch failed three reviews.
- These guides reach every repository that uses Chitty, so the wording names no language or library.
- No property for this ticket: it changes fixed text, with no input to generate.

Planning guide. In `src/chitty/roles/plan.md`, replace the bullet beginning `Compare each decision in the description` with this block, exactly as written (it is already wrapped):

```markdown
- Specify property tests by default. Compare each decision in the description
  with the criteria, because workers test what criteria name. For each
  behaviour, write the property and what the test generates: the inputs and
  the state the behaviour depends on, such as files present, branches and
  config. For example, "for any criteria list and valid N, only criterion N
  changes", or "for any set of directories, each on disk, only on another
  branch, or both, `show` finds every ticket".
- Name the repository's property-testing tool. Generated means many inputs
  drawn by that tool, not a few hand-picked cases. If the repository has no
  such tool, say whether the ticket adds one.
- When a behaviour has no property, give the reason in one line. Valid
  reasons: fixed text with no input, such as a docs-only change; a small fixed
  set, with every member listed in the ticket and each one tested; or
  behaviour that needs real external processes, with why no pure core can be
  taken out of it and given properties.
- Say which test must fail without the fix, because a nearby test may already
  pass.
<!-- property-signals -->
- Where behaviour can be a pure function, taking values and returning values
  with no file, network or clock access inside it, have the ticket name that
  function and state its properties: it is far easier to test. A function,
  module or internal API (such as a facade) the ticket names is an internal
  surface and part of its spec, so its tests may call it directly.
```

Shared signal list. Create `src/chitty/roles/property-signals.md` holding exactly this block, so the list has one copy:

```markdown
- These signal a property:
  - structured input giving structured output;
  - a pair that undoes each other (parse and format, export and import): the
    round trip gives back the input;
  - an old implementation to match (refactor, optimise, "replace X with Y"):
    the new one gives the same results;
  - safe to repeat (retry, dedupe, normalise): doing it twice equals once;
  - order or grouping must not matter (batching, pages, merge);
  - nothing lost or made (split, partition, move): counts and totals match;
  - claims over a set of inputs or states: all, every, each, any, always,
    never, except, unless, unique, sorted, at most;
  - open inputs: free text, Unicode, dates and time zones, paths, user files,
    nested data;
  - parsers and validators: any input gives a result or a clear error, never
    a crash;
  - status changes and sequences of operations that must keep a rule;
  - limits: results stay in a range, or more input never gives less output;
  - a bug in an edge case (empty, zero, duplicate, boundary): the examples
    missed part of the inputs.
```

- In `guide()` in `src/chitty/store.py`, replace a line that is exactly `<!-- property-signals -->` in a role file with the contents of `property-signals.md`, before the ticket prefix is added. `property-signals` is not a role: leave `ROLE_NAMES` alone, so `chitty guide property-signals` still fails as an unknown role.
- In `src/chitty/roles/cold-read.md`, add the line `<!-- property-signals -->` after the bullet beginning `Try behaviour rather than assume`, and add this report bullet after the `Surviving mutants` bullet:

```markdown
- Missed properties: behaviour tested only by example where a signal above
  fits, state the tests never vary (files present, branches, config), a reason
  for having no property that does not hold, and logic that could be a pure
  function but is not specified as one. Give each property and what to
  generate, or `none`.
```

- Tests compare text after collapsing runs of whitespace to one space, so line wrapping cannot break them.
- Out of scope: `PLAN.md`, already updated on `main`; `src/chitty/roles/work.md` and `review.md`; and checking tickets mechanically for these words.

## Acceptance Criteria

- [ ] A test in `tests/test_guide_property_tests.py` shows that `chitty guide plan` contains the planning block, with its `<!-- property-signals -->` line replaced by the shared signal list, after collapsing whitespace, and no longer contains `Compare each decision in the description with the criteria, because workers test what criteria name. Say which` (the old bullet). It fails today.
- [x] A test in the same file shows that `chitty guide cold-read TASK-1` contains the shared signal list and the `Missed properties` bullet, after collapsing whitespace, and that neither guide prints `<!-- property-signals -->`. It fails today.
- [x] A test in the same file reads the files in `src/chitty/roles/` and shows that only `property-signals.md` contains `These signal a property`, that `plan.md` and `cold-read.md` each contain the line `<!-- property-signals -->`, and that no role file matches `python|pytest|unittest|quickcheck|fast-check|jest` (case-insensitive). It fails today.

## Plan

Add tests in tests/test_guide_property_tests.py first and confirm they fail against current behavior. Cover both generated guides after whitespace normalization and scan role files for the shared-block markers, unique signal-list source, and language/tool-specific terms. Implement the exact planning and cold-read text, add the shared property-signals.md block, and expand its marker in store.guide before applying the ticket prefix; leave ROLE_NAMES unchanged. Run the focused test to verify the regression, then make format and make check pass, inspect the diff/status, commit implementation files with Task: TASK-302, and update verified criteria and handoff before review.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-302/1`. Check it against the current criteria; do not trust it. Its criterion 3 is not yet a test (copying the list into both role files passes its tests), its pure-function sentence predates the internal-surface wording, and its `PLAN.md` change is superseded by `main`: leave `PLAN.md` alone.

Regression tests failed before implementation (two missing shared-file errors and one missing-source assertion), then passed. make format and make check passed, including all 517 Python test suites and Node tests. chitty fix reported existing task-text warnings only.

Review failed (tests): Add the missing pure-function and internal-surface bullet to the planning guide and extend the planning test to assert the complete specified block, including the signal list in its specified position.
1: fail - `.venv/bin/chitty guide plan | grep -F 'Where behaviour can be a pure function'` printed no match; `.venv/bin/python -m unittest tests.test_guide_property_tests -v` printed OK despite the missing required bullet, so the test does not verify the entire planning block.
2: pass - The focused test printed OK; against an archived `main` source tree it raised FileNotFoundError for the missing shared list, and the specified signal and report text are present.
3: pass - The focused test printed OK; against archived `main` it failed with `[] != ['property-signals.md']`. `make format && make check` passed with 517 tests OK and Node tests passing.

## Summary

Implemented and committed as 140bade (Task: TASK-302). Shared property signals expand in plan and cold-read guides before ticket prefixing; ROLE_NAMES remains unchanged. Verified all three criteria with tests/test_guide_property_tests.py, then make format and make check. No follow-up work.

## History

- 2026-11-12T18:38:04Z kind-yellow-vole → backlog
- 2026-11-12T19:53:21Z kind-yellow-vole: changed title, owner, description, acceptance criteria
- 2026-11-12T19:53:21Z kind-yellow-vole backlog → planning
- 2026-11-12T19:53:34Z kind-yellow-vole planning → cold-read
- 2026-11-12T19:56:03Z kind-yellow-vole: changed description, acceptance criteria
- 2026-11-12T19:56:03Z kind-yellow-vole cold-read → planning
- 2026-11-12T19:56:04Z kind-yellow-vole planning → cold-read
- 2026-11-12T19:58:06Z kind-yellow-vole: changed description, acceptance criteria, notes
- 2026-11-12T19:58:06Z kind-yellow-vole cold-read → planning
- 2026-11-12T20:18:19Z kind-yellow-vole: changed description, acceptance criteria
- 2026-11-12T20:18:41Z kind-yellow-vole: replaced notes; changed acceptance criteria
- 2026-11-12T20:18:55Z kind-yellow-vole planning → cold-read
- 2026-11-12T20:24:25Z kind-yellow-vole: changed acceptance criteria, notes
- 2026-11-12T20:24:25Z kind-yellow-vole cold-read → planning
- 2026-11-12T20:59:55Z kind-yellow-vole: replaced notes; changed owner, description, acceptance criteria
- 2026-11-12T20:59:55Z kind-yellow-vole planning → todo
- 2026-11-12T21:30:14Z kind-yellow-vole: changed description
- 2026-11-12T21:34:10Z able-ginger-urchin todo → doing
- 2026-11-12T21:34:32Z able-ginger-urchin: wrote the plan
- 2026-11-12T21:37:15Z able-ginger-urchin: changed notes, summary; ticked acceptance criteria
- 2026-11-12T21:37:15Z able-ginger-urchin doing → review
- 2026-11-13T08:52:39Z mellow-ebony-marten: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-13T08:52:39Z mellow-ebony-marten review → doing
