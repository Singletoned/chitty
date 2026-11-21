---
title: Generate multi-ticket placements for ticket reads
status: planning
depends_on:
  - TASK-522
created: 2026-11-21
---

## Description

`TASK-393` and `TASK-522` check every placement of one ticket in every checkout kind with fixed dates. This ticket adds a generated property for interactions they cannot reach: several tickets in one repository, both contexts, tickets archived on `main`, commit dates out of causal order, and decoy branches.

Draft, to be replanned against the builder that `TASK-393` and `TASK-522` land in `tests/ticket_placements.py`. Do not move to `todo` before that.

- `test_generated_placements` in `tests/test_property_ticket_reads.py`, Hypothesis with `deadline=None`, `max_examples=40`, `derandomize=True`, `database=None`. Each example builds one repository with `make_repo`.
- Draw 1 to 4 tickets. Each has a distinct number, never equal to a decoy's number, a context (`tasks` or `human`), whether it is archived on `main` (for placements on `main`), and a placement from `st.sampled_from(PLACEMENTS)`. Draw one checkout kind for the read, compatible with every drawn placement or redrawn. Draw commit dates at random, so commit order differs from causal order. Add decoy branches at random: for `TASK-5`, `task-50`, `TASK-5` and `feature/task-5`.
- Where a ticket's file exists in the reading checkout, draw whether to make an uncommitted edit there.
- Expected per ticket: the same table as `TASK-393` and `TASK-522`, by placement and kind. Compare `Repo.find` per ID. `Repo.tasks` for each context raises when any drawn ticket in it has an error result; otherwise it lists exactly the expected tickets.
- Builder changes the replan must settle: `place` taking a context, an archived flag and a date source; placement (f) sharing one `other` branch between tickets; (j) and (l) fast-forward merging while other tickets have moved `main`.
- A mutant test: the swapped-`contains` mutant from `TASK-393` makes the property fail.

## Acceptance Criteria

- [ ] `test_generated_placements` passes and compares `Repo.find` and `Repo.tasks` against the expected table for every drawn ticket
- [ ] The swapped-`contains` mutant test shows the property fails under the mutant; `make check` passes

## Notes

Split from `TASK-393` on 2026-11-21. Keep in planning until `TASK-522` lands; then replan against the landed builder and cold-read.

## History

- 2026-11-21T23:05:47Z lively-zinc-newt → planning
