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

- Property: for any mapping of 1 to 4 provisional IDs (`TASK-` plus six capital letters) to numeric IDs, and any `Frontmatter` with fixed valid `title`, `status` and `created`, whose `parent` and `depends_on` entries are each drawn from the mapping keys, other IDs not in the mapping, or absent (`depends_on` may hold entries that differ only in letter case), with each ID written in random letter case: `blocking_link` returns the parent match when the parent is a key, else the first matching `depends_on` entry, else `None`. Compute the expected result from the drawn values directly. No Git repository.
- Two committed mutant tests in the same file: one `blocking_link` that compares the raw `str` values case-sensitively against `str(key)`, and one that ignores `parent`. Run the property body against each mutant and assert it raises `AssertionError`.

Before implementing, add the function raising `NotImplementedError` and confirm the property fails; then implement and run `make check`.

## Acceptance Criteria

- [ ] The `blocking_link` property passes, and fails against the `NotImplementedError` stub
- [ ] Both committed mutant tests pass, showing the property fails for the case-sensitive mutant and for the mutant that ignores `parent`; `make check` passes

## History

- 2026-11-21T23:15:28Z lively-zinc-newt → todo
- 2026-11-21T23:15:36Z lively-zinc-newt todo → cold-read
