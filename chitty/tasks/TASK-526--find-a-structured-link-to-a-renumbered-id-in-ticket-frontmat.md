---
title: Find a structured link to a renumbered ID in ticket frontmatter
status: cold-read
parent: TASK-391
created: 2026-11-21
---

## Description

Split from `TASK-519` on 2026-11-21. `TASK-519` refuses a provisional renumbering plan when an untouched ticket's structured link points at an ID the plan would change. This ticket adds only the pure comparison it uses; nothing calls it yet.

Add `blocking_link(frontmatter: Frontmatter, mapping: Mapping[TaskId, TaskId]) -> tuple[TaskId, str] | None` to `src/chitty/renumbering.py` (a pure module). It returns `(TaskId.parse(parent), "parent")` if `frontmatter.parent` is set and parses to a key of `mapping`; else `(old, "depends_on")` for the first `frontmatter.depends_on` entry whose `TaskId.parse` is a key; else `None`. `parse` already rejects link values that are not task IDs, and `TaskId.parse` ignores case (`task-aaaaaa` is `TASK-AAAAAA`).

Tests in `tests/test_property_renumbering.py`, Hypothesis (the repository's property tool):

- Write the check as a plain helper `check_blocking_link(fn, case)` that builds the `Frontmatter`, calls `fn(frontmatter, mapping)` and asserts the result. The property `test_blocking_link` is `@given(cases())` calling `check_blocking_link(blocking_link, case)`. No Git repository.
- `cases()` draws a mapping of 1 to 4 distinct provisional IDs (`TASK-` plus six capital letters) to distinct numeric IDs. Each link is drawn with a label: `("key", k, spelling)`, where `k` is a mapping key and `spelling` is `str(k)` with each letter's case drawn at random; `("other", spelling)`, an ID not in the mapping (another provisional ID or a numeric `TASK-<n>`); or absent. `parent` is one such link; `depends_on` is a list of 0 to 4 such links, whose spellings must be distinct strings (two spellings of one key are allowed). `Frontmatter` gets fixed valid `title`, `status` and `created`.
- Expected result, from the labels only (never by calling `TaskId.parse`): if `parent` is labelled `key`, `(k, "parent")`; else the first `depends_on` entry labelled `key`, `(k, "depends_on")`; else `None`. This covers a parent that is not a key followed by a matching `depends_on` entry.
- Add `@example`s so these always run: a parent key spelled in lower case, one in mixed case, a parent key together with a different `depends_on` key, and an `other` parent followed by a `depends_on` key.
- Mutant tests: `mutant_case_sensitive` compares the raw `str` values against `str(key)`; `mutant_ignores_parent` checks only `depends_on`. Each mutant test runs `@given(cases())` with the same examples, calling `check_blocking_link(mutant, case)`, wrapped as `with self.assertRaises(AssertionError): ...` around a call of the inner Hypothesis test (or `find` the failing case with `hypothesis.find` and assert it exists); either way the test passes only when the mutant is caught.

Before implementing, add the function raising `NotImplementedError` and confirm the property fails; then implement and run `make check`.

## Acceptance Criteria

- [ ] The `blocking_link` property passes, and errors with `NotImplementedError` against the stub (reviewer checks that message in the output)
- [ ] Both committed mutant tests pass, showing the property fails for the case-sensitive mutant and for the mutant that ignores `parent`; `make check` passes

## History

- 2026-11-21T23:15:28Z lively-zinc-newt → todo
- 2026-11-21T23:15:36Z lively-zinc-newt todo → cold-read
- 2026-11-21T23:16:47Z lively-zinc-newt: changed description, acceptance criteria
