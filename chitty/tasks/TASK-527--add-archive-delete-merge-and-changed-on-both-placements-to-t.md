---
title: Add archive, delete, merge and changed-on-both placements to the ticket-read matrix
status: doing
depends_on:
  - TASK-393
parent: TASK-393
created: 2026-11-21
---

## Description

Split from `TASK-393` on 2026-11-21 so each part fits one worker session. `TASK-393` adds the placement builder `tests/ticket_placements.py` and placements (a) to (f) and (i), checked from the main checkout in `tests/test_ticket_placement_reads.py`. This ticket adds the remaining six placements to the same module and test: (g), (h), (j), (k), (l) and (m).

Their definitions, base commits, fixture commands and expected results are in `TASK-393`'s Description (read it with `chitty show TASK-393`, archived once done); follow them exactly. In short, read from the main checkout: (g) archived on its local branch shows `branch`, archived; (h) deleted on its local branch is not listed; (j) merged then `main` edited shows `main-2`, or `uncommitted` with an uncommitted edit; (k) raises `changed on both`, with `Expected.errors` holding the backticked strings `` `TASK-<n>` ``, `` `task-<n>` `` and `` `main` ``; (l) merged with `origin/task-<n>` ahead shows `remote`; (m) raises `changed on both`, with `Expected.errors` holding `` `origin/task-<n>` `` and `` `main` `` (backticks included, so `` `task-<n>` `` from (k) cannot match inside `origin/task-<n>`). With an uncommitted edit in the main checkout, among these six only (j) changes ((a) also changes, as landed). A planner probe on `main` (2026-11-21) confirmed each.

Landed code (rechecked on `main` 2026-11-21): `tests/ticket_placements.py` has `PLACEMENTS`, `Expected(title, archived=False, errors=())`, `git`, `make_repo`, `write_ticket(root, number, title)` (active path only), `edit_uncommitted`, `commit(root, day)` (dates `2026-01-<day>`) and `place`, which commits the base on day 1 and branch work on days 2 and 3. `test_main_checkout_placements` in `tests/test_ticket_placement_reads.py` decides the uncommitted-edit title with `placement == "a"`; extend that to `placement in ("a", "j")`. For (g), on `task-<n>` set the title to `branch` and `git mv` the file into `chitty/tasks/archive/`, in one commit; delete (h) with `git rm` on the branch; merge (j), (l) with `git merge --ff-only task-<n>` on `main`; later `main` edits use day 4 or later, so commit dates stay increasing. Add the six names to `PLACEMENTS` and their cases to `place`; `test_main_checkout_placements` then loops over all 13 placements and the 11 uncommitted-edit variants. No production code changes unless a test finds a bug; then fix it here and keep the failing case as an explicit test. No property: a fixed set of placements, each listed and tested; generated draws are `TASK-523`.

## Acceptance Criteria

- [ ] `test_main_checkout_placements` covers all 13 placements and the 11 uncommitted-edit variants and passes. A note records two wrong-expectation runs, each made by temporarily editing `place` and then reverted: (j) expecting `branch` makes the (j) subTests fail, and (m) expecting (k)'s errors makes the (m) subTest fail
- [ ] `make check` passes

## Plan

Extend the Git placement builder and edited-checkout expectations, verify both requested wrong expectations fail, then run formatting and checks.

## Notes

Keep in planning until its dependency lands; then compare with the landed code, cold-read and move to `todo`.

Replanned 2026-11-21 after `TASK-393` landed.

Wrong-expectation runs: expecting branch for j failed j without edit (the edited variant deliberately expects uncommitted); expecting k errors for m failed both m variants. Both changes were reverted.

## Summary

Added six placement fixtures and main-checkout coverage. Both wrong-expectation runs failed as recorded; make check passed 1034 tests.

## History

- 2026-11-21T23:18:35Z lively-zinc-newt → todo
- 2026-11-21T23:18:53Z lively-zinc-newt: changed notes
- 2026-11-21T23:18:53Z lively-zinc-newt todo → planning
- 2026-11-21T23:53:00Z lively-zinc-newt: changed description, notes
- 2026-11-21T23:53:00Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:54:54Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:54:54Z lively-zinc-newt cold-read → todo
- 2026-11-22T00:06:29Z zesty-bronze-stoat todo → doing
- 2026-11-22T00:07:58Z zesty-bronze-stoat: wrote the plan
- 2026-11-22T00:09:03Z zesty-bronze-stoat: changed notes
- 2026-11-22T00:10:19Z zesty-bronze-stoat: changed summary
