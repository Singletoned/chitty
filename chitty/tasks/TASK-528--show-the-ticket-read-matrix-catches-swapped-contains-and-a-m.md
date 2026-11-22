---
title: Show the ticket-read matrix catches swapped `contains` and a missing `main_tip`
status: doing
depends_on:
  - TASK-527
parent: TASK-393
created: 2026-11-21
---

## Description

Split from `TASK-393` on 2026-11-21. After `TASK-527`, `tests/test_ticket_placement_reads.py` checks all 13 placements read from the main checkout. This ticket adds two mutant tests showing those checks catch wiring bugs in `Repo._choose_source` (`src/chitty/store.py`).

In the style of `test_mutant_ignores_current_branch` in `tests/test_source_copy_checkouts.py`: patch `chitty.store.ticket_source` with a wrapper around the real function, which `Repo._choose_source` calls with nine positional arguments. (1) Swapped `contains`: replace the 8th argument `contains` with `lambda a, b: contains(b, a)`. (2) `main_tip=None`: replace the 5th argument with `None`. Factor the checks as follows (decided 2026-11-22):

- In `tests/test_ticket_placement_reads.py`, add a module-level function `placement_mismatches(parent: Path) -> list[str]`. For every placement in `PLACEMENTS` and every edit variant used by `test_main_checkout_placements` (`edit` in `(False, True)`, except only `False` for `f` and `i`), it builds a fresh repository under `parent` with `make_repo` and `place(root, placement, 5)`, applies `edit_uncommitted` when `edit`, picks the title with the same rule as today (`"uncommitted" if edit and placement in ("a", "j") else expected.title`), and compares `Repo.find(TASK-5)` and `Repo.tasks(context("tasks"), "all")` with the expected result. It appends one string `"<placement> edit=<edit>: <what differed>"` for each difference: a wrong title or archived flag from `find` or in the listing; for an error placement, `find` or `tasks` not raising `ChittyError` or its message lacking an expected substring; for a not-listed placement, `find` not raising `ChittyError` containing `no task`, or `tasks` not returning `[]`. It catches only `ChittyError`; any other exception propagates.
- Rewrite `test_main_checkout_placements` as `self.assertEqual(placement_mismatches(self.tmp), [])`, which reports every difference in one failure message. This replaces its `subTest` loop; the checks themselves are the same.
- `test_mutant_swapped_contains` and `test_mutant_no_main_tip` each patch `chitty.store.ticket_source` with their wrapper and assert `placement_mismatches(self.tmp)` is non-empty.

A planner probe on `main` (2026-11-21) showed swapped `contains` changes most placements, and `main_tip=None` changes (j) (it shows `branch` instead of `main-2`). A cold reader's probe (2026-11-22): 0 mismatches with no mutant, 32 with swapped `contains` (placements b, c, d, e, g, h, j, l), 4 with `main_tip=None` (all at (j)).

## Acceptance Criteria

- [ ] With no mutant, `placement_mismatches` returns `[]` and the rewritten `test_main_checkout_placements` passes; both mutant tests pass, each getting a non-empty list; `make check` passes

## Plan

Extract the placement comparison into a mismatch collector, then exercise it with two ticket_source wiring mutants and run the project checks.

## Notes

Keep in planning until its dependency lands; then compare with the landed code, cold-read and move to `todo`.

`TASK-527` landed 2026-11-22: `PLACEMENTS = tuple("abcdefghijklm")` on `main`.

## History

- 2026-11-21T23:18:39Z lively-zinc-newt → todo
- 2026-11-21T23:18:57Z lively-zinc-newt: changed notes
- 2026-11-21T23:18:57Z lively-zinc-newt todo → planning
- 2026-11-22T00:16:50Z lively-zinc-newt: changed notes
- 2026-11-22T00:16:50Z lively-zinc-newt planning → cold-read
- 2026-11-22T00:18:12Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T00:18:12Z lively-zinc-newt cold-read → todo
- 2026-11-22T00:35:24Z upbeat-khaki-quail todo → doing
- 2026-11-22T00:37:14Z upbeat-khaki-quail: wrote the plan
