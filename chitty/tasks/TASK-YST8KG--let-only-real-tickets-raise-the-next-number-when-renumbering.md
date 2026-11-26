---
title: Let only real tickets raise the next number when renumbering
status: done
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

### Why

On 2026-11-25 `chitty renumber` on `main` gave this repository's provisional tickets `TASK-10000` onwards, though the highest real ticket was `TASK-692`. `Repo._plan_provisional_renumbering` (`src/chitty/store.py`) reserves every number mentioned in any ticket's text (`self._reserve_numbers(used, ids.ticket_references(path.read_text(), used.keys()))`) as if it were used, and `plan_renumbering` (`src/chitty/renumbering.py`) starts at `max(used) + 1`. An archived ticket mentions a placeholder `TASK-9999`, so one mention moved every later number. Decided (the person, 2026-11-26): only real tickets raise the next number. `TASK-10000` onwards stay as they are.

### Change

- `plan_renumbering(used, provisional, *, avoid)` gets a required keyword argument `avoid: Mapping[str, set[int]]`: numbers mentioned in text. It still starts after `max(used)` per prefix (0 when none), counts up, and skips any number in `used` or `avoid`. Mentions never raise the start.
- In `_plan_provisional_renumbering` (the `plan_renumbering` call in `src/chitty/store.py`), `used` stays as today (`_used_numbers`, including deleted numbers, plus `self.ticket_ids()`); the numbers from `ids.ticket_references` over file text go into a separate `avoid` mapping instead. A mention of a number that is not a real ticket therefore never gets that number reused, as today.

### Out of scope

Renumbering `TASK-10000` onwards back down; treating mentions of other repositories' tickets differently (TASK-QYMMZY); `next_number` and `new_id`, which already count only files.

## Acceptance Criteria

- [x] In `tests/test_property_renumbering.py`, a Hypothesis property test of `plan_renumbering` draws `used` and `avoid` number sets for one prefix (with `avoid` numbers both below and above `max(used)`, including very large ones such as 9999) and 1 to 5 provisional IDs. The new numbers are distinct and above `max(used)` (or from 1 when `used` is empty), none is in `used` or `avoid`, they follow the sorted provisional IDs in increasing order, and every number from `max(used) + 1` up to the largest new number is either new or in `avoid`. That file already defines its own `examples` decorator, so import the example-count helper as `from tests import examples as example_count` and use `@settings(max_examples=example_count(N))`. A fixed case, `used={1}`, `avoid={9999}`, one provisional ID, gives number 2; it fails today because mentions raise the start.
- [x] In `tests/test_renumber_provisional.py`, on `main`, with real ticket `TASK-1` whose Description mentions `TASK-9999` and `TASK-2` (written into its file directly, as the existing fixtures cannot add that text) and one provisional ticket, `chitty renumber` gives the provisional ticket `TASK-3`, not `TASK-10000` (today) or `TASK-2`. Fails without the change. Regression tests: the existing renumbering tests pass after passing `avoid={}` at each `plan_renumbering` call. `make check` passes.

## Plan

Add property and CLI regression tests and verify they fail; separate mentioned numbers from used numbers in renumbering, skip mentions during allocation, then format and run checks.

## Notes

Before the fix the CLI regression produced TASK-10000 instead of TASK-3; the fixed planner case failed because the required avoid argument did not exist.

The example-count enforcement test assumed the helper is always named examples; updated it to recognize imports aliased from tests, as required by this ticket.

Reviewed: Changes meet both criteria.
1: pass - make check passes; applying the property and fixed-case tests to the merge-base and running pytest produced TypeError for the missing avoid argument, while both pass with the change.
2: pass - make check passes (1240 tests); applying the CLI test to the merge-base and running pytest produced TASK-10000 instead of TASK-3, while it passes with the change.

## Summary

Renumbering starts after real used IDs and skips numbers mentioned in ticket text. Added property and CLI regression coverage; the CLI test failed with TASK-10000 before the fix. make check passes.

## History

- 2026-11-26T10:54:41Z calm-ochre-quail → backlog
- 2026-11-26T10:54:44Z calm-ochre-quail: changed notes
- 2026-11-26T10:56:45Z calm-ochre-quail: changed labels
- 2026-11-26T11:11:25Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:25Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:16:15Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:16:15Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:17:28Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T11:17:28Z calm-ochre-quail cold-read → todo
- 2026-11-26T11:23:24Z golden-fawn-dormouse todo → doing
- 2026-11-26T11:28:09Z golden-fawn-dormouse: wrote the plan
- 2026-11-26T11:28:48Z golden-fawn-dormouse: changed notes
- 2026-11-26T11:33:31Z golden-fawn-dormouse: changed notes
- 2026-11-26T11:36:18Z golden-fawn-dormouse: changed summary
- 2026-11-26T11:39:34Z golden-fawn-dormouse doing → review
- 2026-11-26T11:48:26Z friendly-ginger-urchin: changed notes; ticked acceptance criteria
- 2026-11-26T11:48:26Z friendly-ginger-urchin review → done
