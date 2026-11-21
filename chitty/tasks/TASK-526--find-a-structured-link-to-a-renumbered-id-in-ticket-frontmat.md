---
title: Find a structured link to a renumbered ID in ticket frontmatter
status: doing
parent: TASK-391
created: 2026-11-21
---

## Description

Split from `TASK-519` on 2026-11-21. `TASK-519` refuses a provisional renumbering plan when an untouched ticket's structured link points at an ID the plan would change. This ticket adds only the pure comparison it uses; nothing calls it yet.

Add `blocking_link(frontmatter: Frontmatter, mapping: Mapping[TaskId, TaskId]) -> tuple[TaskId, str] | None` to `src/chitty/renumbering.py` (a pure module). It returns `(TaskId.parse(parent), "parent")` if `frontmatter.parent` is set and parses to a key of `mapping`; else `(old, "depends_on")` for the first `frontmatter.depends_on` entry whose `TaskId.parse` is a key; else `None`. `parse` already rejects link values that are not task IDs, and `TaskId.parse` ignores case (`task-aaaaaa` is `TASK-AAAAAA`).

Tests in `tests/test_property_renumbering.py`, Hypothesis (the repository's property tool), as methods of its `TestRenumberingProperties` class with module-level helpers, using `@settings(deadline=None)` as that file does. If `assume()` makes Hypothesis report `filter_too_much`, draw `other` suffixes from those not in the mapping instead.

- Write the check as a plain helper `check_blocking_link(fn, case)` that builds the `Frontmatter`, calls `fn(frontmatter, mapping)` and asserts the result. The property `test_blocking_link` is `@given(cases())` calling `check_blocking_link(blocking_link, case)`. No Git repository.
- `cases()` draws a mapping of 1 to 4 distinct provisional IDs (`TASK-` plus a suffix drawn as `provisional_suffix` in `src/chitty/ids.py` draws it: letters from `PROVISIONAL_LETTERS` and digits from `PROVISIONAL_DIGITS`; call it with an adapter `lambda n: draw(st.integers(0, n - 1))` inside the `cases()` composite. It always includes a letter, so a suffix never parses as a number) to distinct numeric IDs. Each link is drawn with a label: `("key", k, spelling)`, where `k` is a mapping key and `spelling` is `str(k)` with each letter's case drawn at random; `("other", spelling)`, another provisional ID or a numeric `TASK-<n>`, rejected with `assume()` when `TaskId.parse(spelling)` is a mapping key (IDs ignore case, and Hypothesis often draws equal suffixes); or absent. Draw the label first with `st.sampled_from(("key", "other", None))`, so each is equally likely. `parent` is one such link; `depends_on` is a list of 0 to 4 such links, whose spellings must be distinct strings (two spellings of one key are allowed). `Frontmatter` gets fixed valid `title`, `status` and `created`.
- Expected result, from the labels only (never by calling `TaskId.parse`): if `parent` is labelled `key`, `(k, "parent")`; else the first `depends_on` entry labelled `key`, `(k, "depends_on")`; else `None`. This covers a parent that is not a key followed by a matching `depends_on` entry.
- Add `@example`s so these always run: a parent key spelled in lower case, one in mixed case, a parent key together with a different `depends_on` key, an `other` parent followed by a `depends_on` key, and no parent with two different `depends_on` keys (expecting the first).
- Mutant tests: `mutant_case_sensitive` compares the raw `str` values against `str(key)`; `mutant_ignores_parent` checks only `depends_on`. Each mutant test runs `@given(cases())` with the same examples, calling `check_blocking_link(mutant, case)`, and the mutant test wraps the call of that `@given` function in `with self.assertRaises(AssertionError):`. The `@example`s guarantee each mutant is caught; any other exception propagates and fails the test.

Before implementing, add the function raising `NotImplementedError` and confirm the property fails; then implement and run `make check`.

## Acceptance Criteria

- [ ] Against the `NotImplementedError` stub, `test_blocking_link` errors with `NotImplementedError` (reviewer checks the output); after implementation it passes
- [ ] Both committed mutant tests pass, showing the property fails for the case-sensitive mutant and for the mutant that ignores `parent`; `make check` passes

## Plan

Add the pure link comparison and property-based cases with explicit examples and mutant checks; verify the stub fails first, then format and run the full checks.

## Notes

Stub verification: the focused test errored with NotImplementedError in blocking_link, as required.

## History

- 2026-11-21T23:15:28Z lively-zinc-newt → todo
- 2026-11-21T23:15:36Z lively-zinc-newt todo → cold-read
- 2026-11-21T23:16:47Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:18:08Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:19:14Z lively-zinc-newt: changed description
- 2026-11-21T23:19:14Z lively-zinc-newt cold-read → todo
- 2026-11-21T23:56:27Z plucky-khaki-crane todo → doing
- 2026-11-21T23:58:08Z plucky-khaki-crane: wrote the plan
- 2026-11-21T23:59:00Z plucky-khaki-crane: changed notes
