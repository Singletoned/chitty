---
title: Parse ticket frontmatter with the libyaml C loader
status: todo
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

- [ ] Regression test: a Hypothesis property in `tests/test_model.py` builds tickets with `model.new_task` from drawn `st.text()` title, owner and labels, renders them with `Task.render()`, and asserts that `yaml.load` of the rendered frontmatter gives the same value with `model._StringLoader` as with a reference `yaml.SafeLoader` subclass that has `yaml_implicit_resolvers = {}` (defined in the test). Use `examples(100)` from `tests/__init__.py`
- [ ] A test asserts `issubclass(model._StringLoader, yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader)`, with no skip; it fails before the change
- [ ] `make check` passes

## History

- 2026-11-26T21:56:05Z youthful-lilac-heron → cold-read
- 2026-11-26T22:00:03Z youthful-lilac-heron: changed description, acceptance criteria
- 2026-11-26T22:01:16Z youthful-lilac-heron cold-read → todo
