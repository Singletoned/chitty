---
title: Check main-checkout ticket reads against every branch placement
status: doing
depends_on:
  - TASK-378
  - TASK-480
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-378` and `TASK-480` make `Repo` read each ticket from the place `ticket_source` (`src/chitty/ticket_source.py`) names. `tests/test_ticket_reads.py` and `tests/test_source_copy_checkouts.py` test a few fixed placements. Wiring bugs in `Repo._choose_source` (`src/chitty/store.py`), such as swapped `contains` arguments or a wrong `main_tip`, can hide between them. This ticket adds a placement builder and checks every placement read from the main checkout. Reads from linked worktrees are `TASK-522` and generated multi-ticket draws are `TASK-523` (both split from this ticket); they reuse the builder.

Scope, after a second split on 2026-11-21 (the worker model gave up on the whole matrix in one session): this ticket builds placements (a) to (f) and (i) only, with their expected results and the uncommitted-edit variants for (a) to (e). `TASK-527` adds (g), (h) and (j) to (m); `TASK-528` adds the mutant tests. All 13 definitions and results stay below so the module is designed for them; `PLACEMENTS` here holds only `a` to `f` and `i`.

Out of scope: a missing `main` commit (covered by `tests/test_property_ticket_source.py`), provisional tickets, linked worktrees, more than one ticket, random dates and decoy branches. No production code changes unless a test finds a bug; then fix it here and keep the failing case as an explicit test.

Builder: new module `tests/ticket_placements.py`, importable by later tickets.

- `make_repo(parent: Path) -> Path`: a fresh directory under `parent` (`tempfile.mkdtemp(dir=parent)`), `git init -b main`, local `user.name` and `user.email` (`RepoTestCase` empties `HOME`), and `chitty.toml` holding `CONFIG` from `tests/support.py` (contexts `tasks` and `human`, current `chitty_version`). Commit no placeholder file such as `.gitkeep` in a context directory: it makes every read fail with `task filename '.gitkeep' must end with .md`. Commits pin `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` to fixed increasing dates.
- `PLACEMENTS`: the 13 names `a` to `m` below. `place(root, placement, number)` builds one ticket `TASK-<number>` in context `tasks`, active on `main` wherever it is on `main`, and returns an `Expected` value: either the title the read must show and whether it is archived, `None` for not listed, or the substrings the `ChittyError` must contain. Each copy has a distinct title (`main`, `branch`, `remote`, `uncommitted`, plus `main-2` for a later `main` edit), so the expected source is identified by its title. The expected results are written out by hand in the module, never computed by calling `ticket_source`.
- Base: every placement except (f) and (i) first commits `TASK-<n>` with title `main` on `main`, and every branch or remote ref below starts from that commit (or from a later `main` commit where stated). (f) and (i) never commit the ticket on `main`, so they are the only placements with no file in the main checkout.
- Remote-tracking refs are made with `git update-ref refs/remotes/origin/task-<n> <commit>` (commit on a temporary branch, then delete it); no remote is configured. Archiving moves the file to `chitty/tasks/archive/`. A fast-forward merge is `git merge --ff-only task-<n>` on `main` in the main checkout.
- Placements: (a) only on `main`; (b) edited on local branch `task-<n>`; (c) edited only on `origin/task-<n>` (made with `git update-ref`, no local branch); (d) local branch, with `origin/task-<n>` ahead of it; (e) local and remote diverged; (f) only on an unrelated branch `other`, not on `main`; (g) archived on its local branch; (h) deleted on its local branch; (i) a new uncommitted file in the main checkout only; (j) local branch edited, fast-forward merged into `main`, then `main` edited again (branch behind `main`); (k) edited on its local branch and also on `main` after the split (changed on both); (l) local branch fast-forward merged into `main`, with `origin/task-<n>` ahead of it; (m) edited only on `origin/task-<n>` and also on `main` after the split.
- `edit_uncommitted(root, number)`: sets the title of the ticket's file in that checkout's working tree to `uncommitted`, without committing. Only call it when that file exists there.

Expected results read from the main checkout (checkout kind (1)): (a) `main`; (b) `branch`; (c), (d) `remote`; (e) `ChittyError` naming `task-<n>` and `origin/task-<n>`; (f), (h) not listed; (g) `branch`, archived; (i) `uncommitted`; (j) `main-2`; (k) `ChittyError` naming `TASK-<n>`, `task-<n>` and `main`; (l) `remote`; (m) `ChittyError` naming `TASK-<n>`, `origin/task-<n>` and `main`. With an uncommitted edit in the main checkout, (a) shows `uncommitted` and (j) shows `uncommitted`; every other result is unchanged. A planner probe on 2026-11-21 built every placement on `main` and confirmed each result, including the uncommitted-edit variants. The error messages are ``ticket `TASK-5` has diverged refs: `origin/task-5`, `task-5` `` for (e), and ``ticket `TASK-5` changed on both `<ref>` and `main` `` for (k) and (m). The same probe showed both mutants below change results: swapped `contains` breaks most placements, and `main_tip=None` breaks (j). If a result disagrees, report it rather than change an expectation to fit the code.

Tests: new `tests/test_ticket_placement_reads.py`, a `RepoTestCase`.

- `test_main_checkout_placements`: for each placement, build it with `TASK-5` and check `Repo.open(root).find(TASK-5)` (or `ChittyError` for error results, and `no task` for not listed) and `repo.tasks(repo.context("tasks"), "all")` (raises on error results; else lists exactly the expected ticket or none). Then, for every placement except (f) and (i), where the main checkout has no committed file to edit, repeat in a fresh repository with `edit_uncommitted` applied in the main checkout. Use `subTest(placement=..., edit=...)`.

No property here: one ticket, a fixed set of 13 placements, each listed and each tested; generated draws are `TASK-523`.

## Acceptance Criteria

- [ ] `test_main_checkout_placements` passes, covering placements (a) to (f) and (i) read from the main checkout and the uncommitted-edit variants for (a) to (e), comparing `Repo.find` and `Repo.tasks` against the expected results in the Description; it fails against `NotImplementedError` stubs of `place` and `edit_uncommitted`
- [ ] `make check` passes

## Plan

Build the scoped deterministic Git fixtures and hand-written expectations, then test find and listing for clean and eligible edited checkouts. Verify the tests fail with builder stubs, run chitty fix, format and make check, and commit the implementation.

## Notes

Planning 2026-11-20: `TASK-378` was split; listing (`_tasks_in_location`, the last `_history()` caller) is now `TASK-480`, so this also waits for it.

Planning blocker: the deterministic test requires every compatible placement in checkout kind (1) both with and without an uncommitted edit to the ticket's file, but placement (f) has that file only on unrelated branch `other`: there is no file in the main checkout to edit. Creating it makes an uncommitted main-checkout ticket, like placement (i), while the stated expected result for (f) is not listed. `Repo._collect_ticket_ids` includes working-tree ticket files and `ticket_source` selects the main working tree when there is no matching ticket branch. Please specify whether (f) is excluded from the edit variant or define its fixture and expected result when a file is created. The same feasibility issue applies to random edits in other checkouts without the file; specify the eligibility rule. The remaining requirements were inspected against `src/chitty/store.py`, `src/chitty/ticket_source.py`, and the existing authoritative listing and source-error tests; implementation, mutation evidence and `make check` could not be verified without a consistent test fixture.

Planning blocker: this is too large for one session. The requested real-Git fixture must compose 13 placements for up to four tickets with five checkout kinds, two contexts, archive states, random dates, decoys and working-tree edits; it also requires an exhaustive deterministic matrix and three separately verified mutations. The existing pure source-selector property alone is 361 lines in `tests/test_property_ticket_source.py`, while this ticket additionally constructs and checks real repositories and multi-ticket interactions. Please split the fixture and deterministic placement coverage from generated multi-ticket coverage and mutation evidence into independently reviewable tickets, defining dependencies and allocating the existing acceptance criteria. I inspected the selector call and listing in `src/chitty/store.py` and the selector in `src/chitty/ticket_source.py`; no implementation, mutation runs, or `make check` were performed, so their outcomes remain unverified. No code changes were made.

Replanned 2026-11-21: split into this ticket (builder and main-checkout reads), `TASK-522` (linked worktrees) and `TASK-523` (generated draws), settling the size blocker above. The (f) edit question is settled: (f) and (i) get no uncommitted-edit variant, since the main checkout has no committed file for them.

Runner error (agent): TASK-393 was unchanged; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-393`

Split again 2026-11-21: the worker returned six sessions saying it could not finish in one turn. Later placements are `TASK-527`, mutants `TASK-528`.

Work started: inspected the ticket and existing ticket-read fixtures and updated the plan. Implementation and verification remain unfinished; no code was changed.

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
- 2026-11-21T22:19:33Z zesty-violet-eel todo → doing
- 2026-11-21T22:21:59Z zesty-violet-eel: changed owner, notes
- 2026-11-21T22:21:59Z zesty-violet-eel doing → planning
- 2026-11-21T23:03:33Z lively-zinc-newt: changed title, description
- 2026-11-21T23:06:14Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:06:23Z lively-zinc-newt: changed description, notes
- 2026-11-21T23:06:23Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:07:52Z lively-zinc-newt: changed description
- 2026-11-21T23:07:52Z lively-zinc-newt cold-read → planning
- 2026-11-21T23:08:03Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:09:46Z lively-zinc-newt: changed description
- 2026-11-21T23:09:46Z lively-zinc-newt cold-read → todo
- 2026-11-21T23:13:04Z quick-amber-eel todo → doing
- 2026-11-21T23:15:13Z quick-amber-eel: wrote the plan
- 2026-11-21T23:16:27Z quick-amber-eel: changed notes
- 2026-11-21T23:16:27Z quick-amber-eel doing → error
- 2026-11-21T23:19:03Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-21T23:19:03Z lively-zinc-newt error → todo
- 2026-11-21T23:40:04Z intrepid-umber-jay todo → doing
- 2026-11-21T23:41:31Z intrepid-umber-jay: wrote the plan
- 2026-11-21T23:41:37Z intrepid-umber-jay: changed notes
