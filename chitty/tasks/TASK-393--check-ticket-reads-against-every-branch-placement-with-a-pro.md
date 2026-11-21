---
title: Check ticket reads against every branch placement with a property
status: todo
depends_on:
  - TASK-378
  - TASK-480
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-378` makes `Repo` read each ticket from the place `ticket_source` (`TASK-377`) names and tests a fixed list of placements. Bugs in the wiring (wrong inputs to `ticket_source`, such as `main_tip`, `changed_on_both` or swapped `contains` arguments, or a missed directory) can hide between fixed cases. Add a generated property over placements. Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-378` lands; the mutation targets below exist only then. A missing `main` (rule 3 with no `main` commit) is covered by `TASK-377`'s unit properties, not here. Provisional tickets (rule 1) are not covered here either; a follow-up adds them after `TASK-380` and `TASK-389`.

Decisions:

- New `tests/test_property_ticket_reads.py`, inheriting `RepoTestCase` from `tests/support.py`. Each repository is built fresh in its own subdirectory (`tempfile.mkdtemp(dir=self.tmp)`): `git init -b main`, `git config user.name` and `user.email` (`RepoTestCase` empties `HOME`), and its own `chitty.toml` with contexts `tasks` (`TASK`) and `human` (`HUMAN`) and `chitty_version` set to `CHITTY_VERSION`, as `tests/test_backlog_context.py` sets up. Pin `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` on every commit, drawn at random so commit order differs from causal order.
- Placements, each for one ticket; except (f) and (i), each ticket is on `main`, active or archived, in either context: (a) only on `main`; (b) edited on its local branch; (c) edited only on `origin/<branch>` (`git update-ref`); (d) local branch, with `origin/<branch>` ahead; (e) local and remote diverged; (f) only on an unrelated branch `other`; (g) archived on its local branch; (h) deleted on its local branch; (i) a new uncommitted file in the main checkout only; (j) local branch edited, then merged into `main` by fast-forward, then `main` advanced (the branch is behind `main`); (k) edited on its local branch and also edited on `main` after the branch was made (changed on both); (l) local branch fast-forward merged into `main`, with `origin/<branch>` ahead of it; (m) edited only on `origin/<branch>` and also edited on `main` after the split. Ticket numbers are drawn so they never equal a decoy's number. Decoy branches (`task-50` for `TASK-5`, `TASK-5`, `feature/task-5`) are added at random.
- Checkout kinds: (1) the main checkout; (2) the ticket's own linked worktree (placements with a local branch); (3) another ticket's linked worktree; (4) a linked worktree on branch `feature`, made from `main`'s tip after all `main` commits, so it holds `main`'s copies; (5) a linked worktree with a detached `HEAD` at `main`. Where the ticket file already exists in the reading checkout, at random leave an uncommitted edit to the ticket's file in the reading checkout.
- Expected result, from the placement, not from calling `ticket_source`:
  - in checkout kinds (1), (3), (4), (5): (a) `main`'s content, plus the uncommitted edit only in (1); (b), (g) the local branch's content (archived for (g)); (c), (d) the remote's content; (e) `ChittyError` naming both refs; (f), (h) not listed; (i) listed with its content in (1) only; (j) `main`'s content (plus the uncommitted edit in (1)); (k) `ChittyError` naming the ticket, its branch and `main`; (l) the remote's content (the stale local branch is dropped); (m) `ChittyError` naming the ticket, `origin/<branch>` and `main`;
  - in kind (2), the ticket's own worktree: (b), (g) its working tree, with any uncommitted edit; (h) listed only if the file is present there; (d) the remote's content; (e) and (k) raise as above (rule 6 applies before the working-tree result); (j) `main`'s content, and the worktree's edit does not show; (l) the remote's content.
  - Uncommitted edits in any other checkout never show; decoys never change the result.
- Multi-ticket draws: compare `Repo.find` per ID; `Repo.tasks` must raise when any drawn ticket's expected result is an error, else list exactly the expected tickets.
- Two tests: `test_every_placement_and_checkout` loops over every compatible (placement, checkout kind) pair once, with fixed dates, one ticket in `tasks`, active on `main` where it is on `main`, and a second ticket `TASK-<m>` on its own `task-<m>` branch only for kind (3); in kind (1) it runs each pair without an uncommitted edit and, only when the file already exists, with the uncommitted edit (about 55 repositories, measured at 15 to 25 s), so coverage does not depend on random draws or test order under `unittest-parallel`; and the property `test_generated_placements` (`deadline=None`, `max_examples=40`, `derandomize=True`, `database=None`) drawing 1 to 4 tickets with placements from `st.sampled_from`, a checkout kind, dates and uncommitted edits.

No production code changes unless a test finds a bug; then fix it here, with the failing case kept as an explicit test.

## Acceptance Criteria

- [ ] `test_every_placement_and_checkout` and `test_generated_placements` pass, comparing `Repo.find` and `Repo.tasks` against the expected results in the Description
- [ ] Mutation evidence, recorded in the ticket's notes with the failing test: in `TASK-378`'s call to `ticket_source` in `src/chitty/store.py`, (1) swapping the arguments inside the `contains` callback, (2) passing `Repo._main_branch()` as `current_branch`, and (3) passing `main_tip=None` each make `.venv/bin/python -m unittest tests.test_property_ticket_reads` fail; all reverted afterwards; `make check` passes

## Notes

Planning 2026-11-20: `TASK-378` was split; listing (`_tasks_in_location`, the last `_history()` caller) is now `TASK-480`, so this also waits for it.

Planning blocker: the deterministic test requires every compatible placement in checkout kind (1) both with and without an uncommitted edit to the ticket's file, but placement (f) has that file only on unrelated branch `other`: there is no file in the main checkout to edit. Creating it makes an uncommitted main-checkout ticket, like placement (i), while the stated expected result for (f) is not listed. `Repo._collect_ticket_ids` includes working-tree ticket files and `ticket_source` selects the main working tree when there is no matching ticket branch. Please specify whether (f) is excluded from the edit variant or define its fixture and expected result when a file is created. The same feasibility issue applies to random edits in other checkouts without the file; specify the eligibility rule. The remaining requirements were inspected against `src/chitty/store.py`, `src/chitty/ticket_source.py`, and the existing authoritative listing and source-error tests; implementation, mutation evidence and `make check` could not be verified without a consistent test fixture.

## History

- 2026-11-18T16:38:03Z lively-quartz-crane → backlog
- 2026-11-18T16:39:33Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:33Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:42Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:42:35Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:42:35Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:44:53Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:50:16Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:50:16Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:51:26Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:54:01Z lively-quartz-crane: changed description
- 2026-11-18T17:54:01Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:54:03Z lively-quartz-crane planning → todo
- 2026-11-18T18:01:39Z lively-quartz-crane: changed description
- 2026-11-20T23:04:49Z quick-pearl-lapwing: changed dependencies, notes
- 2026-11-21T20:28:33Z eager-silver-gannet todo → doing
- 2026-11-21T20:31:41Z eager-silver-gannet: changed owner, notes
- 2026-11-21T20:31:41Z eager-silver-gannet doing → planning
- 2026-11-21T22:17:13Z witty-pearl-otter: changed description
- 2026-11-21T22:17:23Z witty-pearl-otter planning → cold-read
- 2026-11-21T22:19:01Z witty-pearl-otter cold-read → planning
- 2026-11-21T22:19:03Z witty-pearl-otter planning → todo
