---
title: Parse ticket frontmatter with the libyaml C loader
status: cold-read
priority: high
created: 2026-11-26
provisional: true
---

## Description

`chitty list` parses every ticket, about 1,100 times on this repository, and `model._load_frontmatter` (`src/chitty/model.py`) uses `_StringLoader`, a subclass of the pure-Python `yaml.SafeLoader`. Measured 2026-11-26 on the 770 ticket files here: 0.49 s with `SafeLoader` against 0.01 s with libyaml's `yaml.CSafeLoader`, which gave identical results.

Change: make `_StringLoader` subclass `yaml.CSafeLoader` when PyYAML was built with libyaml (`yaml.__with_libyaml__`), else `yaml.SafeLoader`. Keep `_StringLoader.yaml_implicit_resolvers = {}` so plain scalars stay strings (`no` stays `"no"`). The C loader takes its resolvers from the Python `Resolver`, so this still works; the property test checks it.

Accepted difference: `frontmatter is not valid YAML: ...` errors from the C loader give the line and column, but not the quoted source line with a caret. No test asserts that text.

Out of scope: the rest of `parse` (pydantic validation, sections, history).

## Acceptance Criteria

- [ ] A Hypothesis property test in `tests/test_model.py` draws frontmatter text (both valid ticket frontmatter and arbitrary `st.text()`) and asserts that `yaml.load` with the new loader returns the same value as with a reference `yaml.SafeLoader` subclass that has `yaml_implicit_resolvers = {}` (defined in the test), or that both raise `yaml.YAMLError`. Use `examples(100)` from `tests/__init__.py`. Regression test: it need not fail before the change
- [ ] A test asserts `issubclass(model._StringLoader, yaml.CSafeLoader)` when `yaml.__with_libyaml__` is true; it fails before the change
- [ ] `make check` passes

## History

- 2026-11-26T21:56:05Z youthful-lilac-heron → cold-read
