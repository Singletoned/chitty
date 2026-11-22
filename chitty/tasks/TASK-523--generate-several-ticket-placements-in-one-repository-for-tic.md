---
title: Generate several ticket placements in one repository for ticket reads
status: cold-read
depends_on:
  - TASK-522
created: 2026-11-21
---

## Description

`TASK-393` and `TASK-522` check every placement of one ticket in each checkout kind, using `tests/ticket_placements.py`. This ticket adds a generated property for several tickets placed in one repository, read from the main checkout, so interactions between tickets' branches and `main` commits are covered. Replanned and split 2026-11-22 against the landed builder; contexts, archiving on `main`, random commit dates, decoy branches, the placements `f`, `i`, `j`, `l` and linked checkouts are a follow-up ticket.

Planner probe 2026-11-22: 150 random cases of two to four tickets with distinct numbers in 1 to 59, each placed in turn with `place(root, placement, number)` from `{a, b, c, d, e, g, h, k, m}`, then `Repo.open(root).find(TaskId("TASK", number))` for each, gave no mismatch against each `place` call's `Expected`. Excluded placements do not compose with unchanged `place`: `f` always creates branch `other`, `i` leaves an uncommitted file that the next `place` commits, and `j` and `l` fast-forward `main`, which fails once another ticket has moved it.

Decisions:

- `test_generated_placements` in `tests/test_ticket_placement_reads.py`, in `TestTicketPlacementReads`. Hypothesis (the repository's property tool), `@settings(max_examples=30, deadline=None, derandomize=True, database=None)`. Draw two to four distinct numbers from `st.integers(1, 59)` and, for each, a placement from `st.sampled_from("abcdeghkm")`. Build one repository with `make_repo(self.tmp)` and call `place` for each ticket in draw order, keeping each `Expected`. Do not change `tests/ticket_placements.py`.
- Expected per ticket, as in `placement_mismatches` (edit `False`): `find` raises `ChittyError` containing every text in `errors` when `errors` is non-empty; raises with `no task` when `title` is `None` and there are no errors; otherwise returns a ticket with that title and `archived` flag.
- `Repo.tasks(repo.context("tasks"), "all")`: when any drawn ticket's `Expected` has errors, it raises `ChittyError`; otherwise it lists exactly the tickets with a non-`None` title, as `(number, title, archived)`, compared as sets.
- Put the comparison in a helper `generated_mismatches(parent: Path, case) -> list[str]` (module level, like `placement_mismatches`), so the mutant test can reuse it.
- Mutant test `test_generated_mutant_swapped_contains`: under the same `patch("chitty.store.ticket_source", mutant)` as `test_mutant_swapped_contains`, `hypothesis.find` over the same strategy finds a case for which `generated_mismatches` is non-empty.

## Acceptance Criteria

- [ ] `test_generated_placements` passes, comparing `Repo.find` per ticket and `Repo.tasks` against each `place` call's `Expected`, as the Description defines
- [ ] `test_generated_mutant_swapped_contains` passes (the property finds a mismatch under the mutant); `tests/ticket_placements.py` is unchanged; `make check` passes

## Notes

Split from `TASK-393` on 2026-11-21. Keep in planning until `TASK-522` lands; then replan against the landed builder and cold-read.

## History

- 2026-11-21T23:05:47Z lively-zinc-newt → planning
- 2026-11-21T23:07:56Z lively-zinc-newt: changed description
- 2026-11-22T09:58:58Z friendly-jade-stoat: changed title, description, acceptance criteria
- 2026-11-22T09:58:58Z friendly-jade-stoat planning → cold-read
