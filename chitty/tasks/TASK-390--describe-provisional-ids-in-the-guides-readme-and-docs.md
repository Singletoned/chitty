---
title: Describe provisional IDs in the guides, README and docs
status: todo
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-389
  - TASK-392
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

## History

- 2026-11-18T16:28:12Z lively-quartz-crane → backlog
- 2026-11-18T16:28:55Z lively-quartz-crane: changed labels, owner, dependencies, description
- 2026-11-18T16:28:55Z lively-quartz-crane backlog → todo
- 2026-11-18T16:34:52Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T16:37:42Z lively-quartz-crane: changed dependencies, description
