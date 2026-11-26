---
title: Let only real tickets raise the next number when renumbering
status: cold-read
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
- In `_plan_provisional_renumbering`, `used` keeps the file numbers and `self.ticket_ids()` (real tickets on disk and on branches); the numbers from `ids.ticket_references` over file text go into a separate `avoid` mapping instead. A mention of a number that is not a real ticket therefore never gets that number reused, as today.

### Out of scope

Renumbering `TASK-10000` onwards back down; treating mentions of other repositories' tickets differently (TASK-QYMMZY); `next_number` and `new_id`, which already count only files.

## Acceptance Criteria

- [ ] In `tests/test_property_renumbering.py`, a Hypothesis property test (`@settings(max_examples=examples(N))`) of `plan_renumbering` draws `used` and `avoid` number sets for one prefix (with `avoid` numbers both below and above `max(used)`, including very large ones such as 9999) and 1 to 5 provisional IDs. The new numbers are distinct and above `max(used)` (or from 1 when `used` is empty), none is in `used` or `avoid`, they follow the sorted provisional IDs in increasing order, and every number from `max(used) + 1` up to the largest new number is either new or in `avoid`. Fails without the change, because `avoid` does not exist and mentions raise the start today.
- [ ] In `tests/test_renumber_provisional.py`, on `main`, with ticket `TASK-1` whose Description mentions `TASK-9999` and `TASK-2`, and one provisional ticket, `chitty renumber` gives the provisional ticket `TASK-3`, not `TASK-10000` (today) or `TASK-2`. Fails without the change. Regression tests: the existing renumbering tests pass after passing `avoid={}` where they call `plan_renumbering`. `make check` passes.

## History

- 2026-11-26T10:54:41Z calm-ochre-quail → backlog
- 2026-11-26T10:54:44Z calm-ochre-quail: changed notes
- 2026-11-26T10:56:45Z calm-ochre-quail: changed labels
- 2026-11-26T11:11:25Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:25Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:16:15Z calm-ochre-quail: replaced notes; changed title, description, acceptance criteria
- 2026-11-26T11:16:15Z calm-ochre-quail to-plan → cold-read
