---
title: Parse ticket frontmatter with the libyaml C loader
status: done
priority: high
created: 2026-11-26
provisional: true
---

## Description

`chitty list` parses every ticket, about 1,100 times on this repository, and `model._load_frontmatter` (`src/chitty/model.py`) uses `_StringLoader`, a subclass of the pure-Python `yaml.SafeLoader`. Measured 2026-11-26 on the 770 ticket files here: 0.49 s with `SafeLoader` against 0.01 s with libyaml's `yaml.CSafeLoader`, which gave identical results.

Change: make `_StringLoader` subclass `yaml.CSafeLoader` when PyYAML was built with libyaml (`yaml.__with_libyaml__`), else `yaml.SafeLoader`. Keep `_StringLoader.yaml_implicit_resolvers = {}` so plain scalars stay strings (`no` stays `"no"`). The C loader takes its resolvers from the Python `Resolver`, so this still works; the property test checks it.

Accepted difference: `frontmatter is not valid YAML: ...` errors from the C loader give the line and column, but not the quoted source line with a caret. No test asserts that text. On malformed YAML the two loaders can also disagree: the C loader accepts some inputs that the Python loader rejects (a tab after `key:`, for example) and rejects a few that it accepts. That is accepted too: Chitty writes only frontmatter that both loaders read the same way, and the property checks exactly that.

Out of scope: the rest of `parse` (pydantic validation, sections, history).

## Acceptance Criteria

- [x] Regression test: a Hypothesis property in `tests/test_model.py` builds tickets with `model.new_task` from drawn `st.text()` title, owner and labels, renders them with `Task.render()`, and asserts that `yaml.load` of the rendered frontmatter gives the same value with `model._StringLoader` as with a reference `yaml.SafeLoader` subclass that has `yaml_implicit_resolvers = {}` (defined in the test). Use `examples(100)` from `tests/__init__.py`
- [x] A test asserts `issubclass(model._StringLoader, yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader)`, with no skip; it fails before the change
- [x] `make check` passes

## Plan

Add a loader-selection test and a rendered-ticket property comparing against a string-only SafeLoader, verify selection fails before the change, then select CSafeLoader when available and run formatting and checks.

## Notes

Decided: restrict generated values to printable nonempty single-line text -> exercise renderable inputs, because existing rendering rejects DEL and NEL; reported separately. Loader-selection test fails before the change as expected.

Decided: generate literal Unicode in the existing provisional-field property -> avoid JSON surrogate escape pairs, because libyaml rejects those malformed YAML escapes while the test targets field validation. The prior check exposed this accepted loader difference.

Reviewed: Loader selection and rendered-ticket equivalence verified.
1: pass - Regression property in tests/test_model.py compares both loaders; make check passes. Printable single-line inputs are a sensible restriction given the reported existing rendering limitations.
2: pass - test_uses_libyaml_when_available passes in make check; in a merge-base worktree with the branch test and PYTHONPATH pointing to its src, pytest reports AssertionError: False is not true.
3: pass - make check: 1298 passed, 684 subtests passed.

## Summary

Uses the libyaml safe loader when available, retaining string-only resolution and the pure Python fallback. Added loader selection and rendered-frontmatter equivalence tests; adjusted the existing provisional property for loader differences. Loader selection failed before the change. make check passed. Reported existing rendering failures for DEL and NEL separately.

## History

- 2026-11-26T21:56:05Z youthful-lilac-heron → cold-read
- 2026-11-26T22:00:03Z youthful-lilac-heron: changed description, acceptance criteria
- 2026-11-26T22:01:16Z youthful-lilac-heron cold-read → todo
- 2026-11-26T23:15:17Z nimble-violet-crane todo → doing
- 2026-11-26T23:19:02Z nimble-violet-crane: wrote the plan
- 2026-11-26T23:19:47Z nimble-violet-crane: changed notes
- 2026-11-26T23:23:59Z nimble-violet-crane: changed notes
- 2026-11-26T23:28:20Z nimble-violet-crane: changed summary
- 2026-11-26T23:30:56Z nimble-violet-crane doing → review
- 2026-11-26T23:38:10Z daring-violet-raven: changed notes; ticked acceptance criteria
- 2026-11-26T23:38:10Z daring-violet-raven review → done
