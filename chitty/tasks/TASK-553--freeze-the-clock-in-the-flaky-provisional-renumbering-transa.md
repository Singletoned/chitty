---
title: Freeze the clock in the flaky provisional-renumbering transaction test
status: doing
labels:
  - bug
priority: high
created: 2026-11-22
---

## Description

`test_transaction` in `tests/test_renumber_provisional.py` is flaky and fails `make check` about once in every run that crosses a second boundary. It computes the expected files with `repo._prepare_renumbering(mapping, writable)` (near line 148) and then calls `repo.renumber_provisional()` (near line 150), which prepares them again. Both stamp the `renumbered from <old ID>` History event with `datetime.now(UTC)`, so when the clock ticks between the two calls the comparison `path.read_text() == task.render()` (near line 159) fails, for example `04:00:00Z` against `03:59:59Z`. Seen 2026-11-22 in the pre-agent check of `TASK-392`, which the runner then marked `error`.

Fix the test, not the code: patch the clock for both calls so they see the same time, for example with `mock.patch("chitty.store.datetime")` returning a fixed `datetime.now(UTC)` (check how `src/chitty/store.py` imports `datetime` first; other tests that freeze time are a precedent, `git grep -n "patch(\"chitty.store.datetime" tests`). Do not change `renumber_provisional` or `_prepare_renumbering`.

To show the fix: temporarily make the clock advance one second between the two calls (for example a fake `now()` that returns increasing times) and confirm the unfixed test fails and the fixed one passes; record that in a note.

## Acceptance Criteria

- [ ] `test_transaction` uses one fixed time for both calls and passes; a note records the unfixed test failing with a clock that advances between the calls; `make check` passes

## Plan

Freeze the store clock across both transaction preparations; reproduce the failure with an advancing clock, verify the fixed test under the same clock, then run make check.

## Notes

An outer mocked store clock advancing one second per now call made the original transaction test fail on the rendered history timestamps (00:00:00 versus 00:00:02); the same invocation passed with the inner fixed clock. make check passed.

## Summary

Froze the store clock across both transaction preparations. Verified the advancing-clock reproduction and ran make check.

## History

- 2026-11-22T04:03:27Z lively-zinc-newt → todo
- 2026-11-22T04:08:05Z witty-jade-quail todo → doing
- 2026-11-22T04:09:52Z witty-jade-quail: wrote the plan
- 2026-11-22T04:11:43Z witty-jade-quail: changed notes, summary
