---
title: Plan provisional renumbering and rewrite ID mentions in pure functions
status: doing
depends_on:
  - TASK-380
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` (`TASK-380`, `TASK-389`), and `chitty renumber` with no path later gives it a sequential number on `main` and rewrites mentions of it (`TASK-391`). This ticket builds only the pure core that command uses, with no caller.

Decisions:

- New module `src/chitty/renumbering.py`. Create it first with these names raising `NotImplementedError`, so the tests fail on behaviour rather than at import.
- `plan_renumbering(used: Mapping[str, set[int]], provisional: Sequence[TaskId]) -> dict[TaskId, TaskId]`. `used` maps each prefix to the sequential numbers already taken in its context (prefixes are unique across contexts: `src/chitty/config.py` rejects duplicates). Each prefix's provisional IDs, in sorted order (`TaskId.__lt__`), get the consecutive numbers starting at `max(used[prefix], default=0) + 1`; a prefix missing from `used` starts at 1 and is not an error; empty `provisional` returns `{}`. Keys are the input `TaskId`s. Errors are `ChittyError` from `chitty.errors`. A provisional ID listed twice raises `ChittyError` naming it: two branches can draw the same suffix. A non-provisional ID (an `int` number) in `provisional` also raises `ChittyError`.
- `replace_ids(text: str, mapping: Mapping[TaskId, TaskId]) -> str` replaces every mention of each old ID in one simultaneous pass (a replaced ID is never replaced again in the same call). A mention is the old ID matched by the ASCII regular expression `(?<![A-Za-z0-9-])<ID>(?![A-Za-z0-9])`, case-sensitive. So mentions after a backtick, `(`, `[`, `"`, `/`, `_` or at line start are rewritten, and so are `TASK-K7Q2MX--slug.md` and `TASK-K7Q2MX-foo`; `XTASK-K7Q2MX`, `-TASK-K7Q2MX`, `TASK-K7Q2MXY` and any form not in exact case, such as the branch name `task-k7q2mx` or `TASK-k7q2mx`, are not. Accepted: such a mention then dangles.
- Which parts of which files `replace_ids` is applied to is `TASK-391`'s decision.

Tests: Hypothesis properties in a new `tests/test_property_renumbering.py`. Generate prefixes matching `[A-Z]+`, sets of used numbers of at least 1 with gaps (so `{1, 5}` must give 6, not 2), provisional IDs from `ids.provisional_suffix` (`TASK-380`) with random draws (deduplicated, except in the duplicate test), and text mixing bounded mentions, look-alikes (each form listed above), lower-case forms and unrelated text. The `replace_ids` oracle is built independently in the test, not by calling the same regular expression: insert known mentions and look-alikes at known places into filler drawn from an alphabet that cannot form an ID (no letters or digits), padding each mention with a separator outside `[A-Za-z0-9-]`. Keep the mapping's keys and values disjoint, as real inputs are (keys provisional, values numeric).

## Acceptance Criteria

- [ ] `plan_renumbering` property: for generated inputs, each prefix's provisional IDs map, in sorted `TaskId` order, onto exactly the consecutive numbers above that prefix's highest used number (or from 1), no new ID is in `used`, and the mapping has one entry per input ID; duplicate or non-provisional input raises `ChittyError`; it fails against the stub
- [ ] `replace_ids` property: in generated text every inserted mention (the form in the Description) becomes its new ID, every look-alike and non-exact-case form is left unchanged, text with no mention is unchanged, and applying it twice equals applying it once; it fails against the stub
- [x] `make check` passes

## Plan

Add the specified pure functions in src/chitty/renumbering.py. Validate duplicate and non-provisional inputs, then allocate per-prefix consecutive IDs in TaskId order. Implement ID rewriting with one combined regex and a single substitution pass. Add Hypothesis property coverage in tests/test_property_renumbering.py, run it against the stubs to verify failure, then implement and run make format and make check.

## Notes

The new property tests were run against the initial NotImplementedError stubs and failed there as expected; after implementation, all five focused tests pass. make check passes all 640 suites, though a pre-existing expected diagnostic from a chitty run test prints during the suite.

Review failed (tests): Expand the properties to exercise the required input and mention cases.
1: fail - Newly found: tests/test_property_renumbering.py always supplies sorted IDs for one prefix at a time, so it does not exercise sorting unsorted input or independent allocation across prefixes. Generate mixed-prefix, shuffled input and check each allocation. In-process NotImplementedError stubs produced 5 errors across the suite.
2: fail - Newly found: the mixed-case suffix example TASK-k7q2mx is never generated: both purported case variants call lower() on the entire ID. Generate an uppercase prefix with a lowercase suffix and assert it remains unchanged. The tests also only use one mapping entry, so generate multiple disjoint mappings and mentions to exercise replacement of each ID in one pass. In-process NotImplementedError stubs produced 5 errors across the suite.
3: pass - make check exited 0, with 640 tests OK, ruff and pyright passing.

## Summary

Implemented pure per-prefix sequential ID allocation and simultaneous boundary-aware ID rewriting in src/chitty/renumbering.py. Added Hypothesis coverage in tests/test_property_renumbering.py. Verified the new tests fail against the initial stubs, then pass after implementation; make check passes all 640 test suites. No follow-up caller work included.

## History

- 2026-11-18T16:20:09Z lively-quartz-crane → backlog
- 2026-11-18T16:23:20Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:28:42Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:30:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:30:08Z lively-quartz-crane backlog → planning
- 2026-11-18T16:30:16Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:30:29Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:34:46Z lively-quartz-crane: changed title, dependencies, description, acceptance criteria
- 2026-11-18T16:34:46Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:34:48Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T16:35:11Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:36:40Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:36:40Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:36:42Z lively-quartz-crane planning → todo
- 2026-11-18T20:28:05Z sunny-dusky-falcon todo → doing
- 2026-11-18T20:29:04Z sunny-dusky-falcon: wrote the plan
- 2026-11-18T20:31:06Z sunny-dusky-falcon: changed notes
- 2026-11-18T20:31:22Z sunny-dusky-falcon: changed summary; ticked acceptance criteria
- 2026-11-18T20:31:24Z sunny-dusky-falcon doing → review
- 2026-11-18T20:33:44Z open-amber-puffin: changed acceptance criteria, notes
- 2026-11-18T20:33:44Z open-amber-puffin review → doing
