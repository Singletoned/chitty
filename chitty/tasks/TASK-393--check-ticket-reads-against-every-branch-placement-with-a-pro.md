---
title: Check ticket reads against every branch placement with a property
status: cold-read
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-378` makes `Repo` read each ticket from the place `ticket_source` (`TASK-377`) names and tests a fixed list of placements. Bugs in the wiring (wrong inputs to `ticket_source`, swapped `contains` arguments, a missed directory) can hide between fixed cases. Add a generated property over placements. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` lands; the mutation targets below exist only then.

Decisions:

- New `tests/test_property_ticket_reads.py`, inheriting `RepoTestCase` from `tests/support.py`. Each example builds a fresh repository in its own subdirectory (`tempfile.mkdtemp(dir=self.tmp)`): `git init -b main`, `git config user.name` and `user.email` (`RepoTestCase` empties `HOME`), and its own `chitty.toml` with contexts `tasks` (`TASK`) and `human` (`HUMAN`), as `tests/test_backlog_context.py` sets up. Settings: `deadline=None`, `max_examples=40`, `derandomize=True`, `database=None`. Pin `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` on every commit, drawn at random so commit order differs from causal order.
- Generate 1 to 4 tickets in either context, each active or archived on `main`, with a placement from `st.sampled_from`: (a) only on `main`; (b) edited on its local branch; (c) edited only on `origin/<branch>` (`git update-ref`); (d) local branch, with `origin/<branch>` ahead; (e) local and remote diverged; (f) only on an unrelated branch; (g) archived on its local branch; (h) deleted on its local branch; (i) a new uncommitted file in the main checkout only. Add decoy branches (`task-50` for `TASK-5`, `feature/task-5`) at random.
- Generate the reading checkout from those compatible with the placements: the main checkout; the linked worktree of a ticket with a local branch ((b), (d), (e), (g), (h)); a checkout of an unrelated branch `feature`; or a detached `HEAD` at `main`. At random, leave an uncommitted edit to each ticket's file in the reading checkout.
- Expected result, from the placement, not from calling `ticket_source`:
  - a non-ticket checkout (main checkout, `feature`, detached): (a) `main`'s content in the main checkout, plus its uncommitted edit there; `main`'s tip content elsewhere; (b), (g) the local branch's content (archived for (g)); (c), (d) the remote's content; (e) raises naming both refs; (f) not listed; (h) not listed; (i) listed with its content in the main checkout only;
  - the ticket's own worktree: (b), (g), (h) its working tree, with any uncommitted edit ((h) not listed unless the file is present); (d) the remote's content; (e) raises;
  - another ticket's worktree: as a non-ticket checkout off `main`.
  - Uncommitted edits elsewhere never show; decoys never change the result. Provisional tickets wait for `TASK-380`.
- Coverage: the property appends each drawn placement and checkout kind to a module-level set; a separate test, `test_every_placement_is_drawn`, run after it in the same class (name it so it sorts later), asserts every placement (a)-(i) and checkout kind appears.

No production code changes unless the property finds a bug; then fix it here, with the failing example kept as an explicit test.

## Acceptance Criteria

- [ ] The property passes over generated placements and checkouts, comparing `Repo.find` and `Repo.tasks` against the expected result in the Description, and `test_every_placement_is_drawn` passes
- [ ] Mutation evidence, recorded in the ticket's notes with the failing assertion: in `TASK-378`'s call to `ticket_source` in `src/chitty/store.py`, swapping the arguments inside the `contains` callback, or passing `Repo._main_branch()` as `current_branch`, makes `.venv/bin/python -m unittest tests.test_property_ticket_reads` fail; both reverted afterwards; `make check` passes

## History

- 2026-11-18T16:38:03Z lively-quartz-crane → backlog
- 2026-11-18T16:39:33Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:33Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:42Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:42:35Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:42:35Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:44:53Z lively-quartz-crane planning → cold-read
