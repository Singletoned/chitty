---
title: Add archive, delete, merge and changed-on-both placements to the ticket-read matrix
status: planning
depends_on:
  - TASK-393
parent: TASK-393
created: 2026-11-21
---

## Description

Split from `TASK-393` on 2026-11-21 so each part fits one worker session. `TASK-393` adds the placement builder `tests/ticket_placements.py` and placements (a) to (f) and (i), checked from the main checkout in `tests/test_ticket_placement_reads.py`. This ticket adds the remaining six placements to the same module and test: (g), (h), (j), (k), (l) and (m).

Their definitions, base commits, fixture commands and expected results are in `TASK-393`'s Description (read it with `chitty show TASK-393`, archived once done); follow them exactly. In short, read from the main checkout: (g) archived on its local branch shows `branch`, archived; (h) deleted on its local branch is not listed; (j) merged then `main` edited shows `main-2`, or `uncommitted` with an uncommitted edit; (k) raises `changed on both` naming `task-<n>` and `main`; (l) merged with `origin/task-<n>` ahead shows `remote`; (m) raises `changed on both` naming `origin/task-<n>` and `main`. With an uncommitted edit in the main checkout, only (j) changes. A planner probe on `main` (2026-11-21) confirmed each.

Add the six names to `PLACEMENTS` and their cases to `place`; `test_main_checkout_placements` then loops over all 13 placements and the 11 uncommitted-edit variants. No production code changes unless a test finds a bug; then fix it here and keep the failing case as an explicit test. No property: a fixed set of placements, each listed and tested; generated draws are `TASK-523`.

## Acceptance Criteria

- [ ] `test_main_checkout_placements` covers all 13 placements and the 11 uncommitted-edit variants and passes; each new placement's check fails if its expected result is changed to the result of a neighbouring placement (for example (j) expecting `branch`), shown once in a note
- [ ] `make check` passes

## Notes

Keep in planning until its dependency lands; then compare with the landed code, cold-read and move to `todo`.

## History

- 2026-11-21T23:18:35Z lively-zinc-newt → todo
- 2026-11-21T23:18:53Z lively-zinc-newt: changed notes
- 2026-11-21T23:18:53Z lively-zinc-newt todo → planning
