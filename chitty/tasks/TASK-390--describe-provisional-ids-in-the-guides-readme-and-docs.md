---
title: Describe provisional IDs in the guides, README and docs
status: done
labels:
  - untestable
owner: nimble-umber-adder
depends_on:
  - TASK-389
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-389`, plain `chitty add` off `main` files the ticket in the default context with a provisional ID (`TASK-K7Q2M`, marked `provisional: true`), and `chitty renumber` with no argument gives provisional tickets sequential numbers on `main` (`TASK-392`). The text that still describes the old rule (worktree adds filed as `BACKLOG`, numbers from every branch) must change. Rule source: `docs/plan/ticket-state.md`, "Planning decisions".

Change:

- `src/chitty/roles/work.md` and `src/chitty/roles/review.md` (the paragraph saying plain `chitty add` files a discovery as `BACKLOG` and that planners should add from the main checkout): a ticket added off `main` gets a provisional ID and `provisional: true`, in the usual context; it is renumbered on `main` later, and its ID works everywhere meanwhile. Keep it general, as `AGENTS.md` requires of the guides.
- `tests/test_cli.py` `test_branch_discoveries_are_filed_in_backlog`, which pins the old guide wording: rename and update it to the new wording.
- `README.md`: the `random_ids` paragraph ("so tickets raised on different branches do not collide") and the `renumber` line.
- `src/chitty/cli.py` help for `renumber` and `move` ("gives the next number"), and `docs/plan/cli.md` for both.
- `docs/plan/principles.md` ("IDs are sequential"): sequential on `main`, provisional elsewhere.

Starts after `TASK-389`; the `renumber` wording after `TASK-392` if that has landed, otherwise leave `renumber` with no argument out.

## Plan

Update the guides, CLI help, README, and plan docs for the ID allocation already shipped by `TASK-389`. Update the existing guide wording test. Omit pathless renumbering until `TASK-392` ships, as the description allows. Verify the shipped allocation modes, guide budgets, and full checks.

## Notes

Decided: pathless renumbering -> omit it, because the ticket explicitly says to leave it out until TASK-392 ships. Removed that dependency so the shipped behavior can be documented now.

Reviewed: wording checked against the ticket.

## Summary

Updated the work/review guides, README, CLI help, and plan docs to explain provisional IDs and distinguish them from sequential and random numeric IDs. Updated the existing guide wording test. No runtime behavior changed. Documented `renumber PATH` only; pathless renumbering is still unshipped (`TASK-392`) and excluded as the ticket allows. `make check` passed all 983 tests; also checked the rendered `move` and `renumber` help.

## History

- 2026-11-18T16:28:12Z lively-quartz-crane → backlog
- 2026-11-18T16:28:55Z lively-quartz-crane: changed labels, owner, dependencies, description
- 2026-11-18T16:28:55Z lively-quartz-crane backlog → todo
- 2026-11-18T16:34:52Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T16:37:42Z lively-quartz-crane: changed dependencies, description
- 2026-11-21T18:46:49Z nimble-umber-adder: changed owner, dependencies; wrote the plan
- 2026-11-21T18:46:49Z nimble-umber-adder todo → doing
- 2026-11-21T18:46:52Z nimble-umber-adder: changed notes
- 2026-11-21T18:50:09Z nimble-umber-adder: changed summary
- 2026-11-21T18:50:09Z nimble-umber-adder doing → review
- 2026-11-22T11:31:15Z human: changed notes
- 2026-11-22T11:31:15Z human review → done
