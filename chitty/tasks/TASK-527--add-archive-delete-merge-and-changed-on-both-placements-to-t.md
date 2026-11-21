---
title: Add archive, delete, merge and changed-on-both placements to the ticket-read matrix
status: cold-read
depends_on:
  - TASK-393
parent: TASK-393
created: 2026-11-21
---

## Description

Split from `TASK-393` on 2026-11-21 so each part fits one worker session. `TASK-393` adds the placement builder `tests/ticket_placements.py` and placements (a) to (f) and (i), checked from the main checkout in `tests/test_ticket_placement_reads.py`. This ticket adds the remaining six placements to the same module and test: (g), (h), (j), (k), (l) and (m).

Their definitions, base commits, fixture commands and expected results are in `TASK-393`'s Description (read it with `chitty show TASK-393`, archived once done); follow them exactly. In short, read from the main checkout: (g) archived on its local branch shows `branch`, archived; (h) deleted on its local branch is not listed; (j) merged then `main` edited shows `main-2`, or `uncommitted` with an uncommitted edit; (k) raises `changed on both` naming `task-<n>` and `main`; (l) merged with `origin/task-<n>` ahead shows `remote`; (m) raises `changed on both` naming `origin/task-<n>` and `main`. With an uncommitted edit in the main checkout, only (j) changes. A planner probe on `main` (2026-11-21) confirmed each.

Landed code (rechecked on `main` 2026-11-21): `tests/ticket_placements.py` has `PLACEMENTS`, `Expected(title, archived=False, errors=())`, `git`, `make_repo`, `write_ticket(root, number, title)` (active path only), `edit_uncommitted`, `commit(root, day)` (dates `2026-01-<day>`) and `place`, which commits the base on day 1 and branch work on days 2 and 3. `test_main_checkout_placements` in `tests/test_ticket_placement_reads.py` decides the uncommitted-edit title with `placement == "a"`; extend that to `placement in ("a", "j")`. Archive (g) with `git mv` into `chitty/tasks/archive/` on the branch; delete (h) with `git rm` on the branch; merge (j), (l) with `git merge --ff-only task-<n>` on `main`; later `main` edits use day 4 or later, so commit dates stay increasing. Add the six names to `PLACEMENTS` and their cases to `place`; `test_main_checkout_placements` then loops over all 13 placements and the 11 uncommitted-edit variants. No production code changes unless a test finds a bug; then fix it here and keep the failing case as an explicit test. No property: a fixed set of placements, each listed and tested; generated draws are `TASK-523`.

## Acceptance Criteria

- [ ] `test_main_checkout_placements` covers all 13 placements and the 11 uncommitted-edit variants and passes; each new placement's check fails if its expected result is changed to the result of a neighbouring placement (for example (j) expecting `branch`), shown once in a note
- [ ] `make check` passes

## Notes

Keep in planning until its dependency lands; then compare with the landed code, cold-read and move to `todo`.

Replanned 2026-11-21 after `TASK-393` landed.

## History

- 2026-11-21T23:18:35Z lively-zinc-newt → todo
- 2026-11-21T23:18:53Z lively-zinc-newt: changed notes
- 2026-11-21T23:18:53Z lively-zinc-newt todo → planning
- 2026-11-21T23:53:00Z lively-zinc-newt: changed description, notes
- 2026-11-21T23:53:00Z lively-zinc-newt planning → cold-read
