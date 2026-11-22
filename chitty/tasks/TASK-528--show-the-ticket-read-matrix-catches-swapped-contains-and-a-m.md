---
title: Show the ticket-read matrix catches swapped `contains` and a missing `main_tip`
status: cold-read
depends_on:
  - TASK-527
parent: TASK-393
created: 2026-11-21
---

## Description

Split from `TASK-393` on 2026-11-21. After `TASK-527`, `tests/test_ticket_placement_reads.py` checks all 13 placements read from the main checkout. This ticket adds two mutant tests showing those checks catch wiring bugs in `Repo._choose_source` (`src/chitty/store.py`).

In the style of `test_mutant_ignores_current_branch` in `tests/test_source_copy_checkouts.py`: patch `chitty.store.ticket_source` with a wrapper around the real function, which `Repo._choose_source` calls with nine positional arguments. (1) Swapped `contains`: replace the 8th argument `contains` with `lambda a, b: contains(b, a)`. (2) `main_tip=None`: replace the 5th argument with `None`. Each test runs the same checks over all placements and collects mismatches: a wrong title or archived flag, a wrong listing, a missing or unexpected `ChittyError`, or a `ChittyError` lacking an expected substring. It asserts at least one mismatch; any other exception propagates and fails the test. Factor the checks so a test can collect mismatches instead of failing on the first, without changing what `test_main_checkout_placements` asserts.

A planner probe on `main` (2026-11-21) showed swapped `contains` changes most placements, and `main_tip=None` changes (j) (it shows `branch` instead of `main-2`).

## Acceptance Criteria

- [ ] Both mutant tests pass, each recording at least one mismatch under its mutant, and `test_main_checkout_placements` still passes unchanged in what it asserts; `make check` passes

## Notes

Keep in planning until its dependency lands; then compare with the landed code, cold-read and move to `todo`.

`TASK-527` landed 2026-11-22: `PLACEMENTS = tuple("abcdefghijklm")` on `main`.

## History

- 2026-11-21T23:18:39Z lively-zinc-newt → todo
- 2026-11-21T23:18:57Z lively-zinc-newt: changed notes
- 2026-11-21T23:18:57Z lively-zinc-newt todo → planning
- 2026-11-22T00:16:50Z lively-zinc-newt: changed notes
- 2026-11-22T00:16:50Z lively-zinc-newt planning → cold-read
