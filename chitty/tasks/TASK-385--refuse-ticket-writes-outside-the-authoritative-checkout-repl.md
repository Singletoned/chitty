---
title: Refuse ticket writes outside the authoritative checkout, replacing the stale-copy guard
status: planning
labels:
  - question
depends_on:
  - TASK-378
  - TASK-382
  - TASK-383
  - TASK-384
  - TASK-393
  - TASK-522
  - TASK-537
  - TASK-547
parent: TASK-376
created: 2026-11-18
---

## Description

Today every ticket write runs `Repo._require_current_version` in `src/chitty/store.py`, which refuses when the newest committed copy of the ticket (by commit time, across every ref) is on another branch: `<ID>'s latest committed version is on branch <b>`. Runner handoffs bypass it with `Edit.skip_current_version`. That guard stopped `chitty run --loop` repeatedly on 2026-11-17 (`TASK-343`, `TASK-364`). Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), each ticket is read from one place (`TASK-378`). Owner decision 2026-11-20: a write is refused only when it would lose or hide a newer copy, not merely because the ticket is read from elsewhere; skipping a branch already in `main` is a reading shortcut, not a rule about writes. `TASK-378` adds the first case of this: in the ticket's own worktree, a write is allowed when `main` has not changed the ticket since the branch split. Replan this ticket around that principle: the property below must expect success in that case too, and each refusal message must say which newer copy the write would lose or hide.

Starts after `TASK-378`, `TASK-382`, `TASK-383`, `TASK-384` and `TASK-393` (whose placement builders the test reuses) land: by then no runner write needs the bypass.

Decisions:

- Replace `_require_current_version(stored)` with `_require_writable(stored)`, called wherever the old guard is: `edit`'s review gate (its condition loses the `skip_current_version` clause), `_set_archived` (so `archive` and `restore`), `_delete_done`, `move` and `_save`. `add` creates a new file, and `renumber PATH` works on duplicate files in this checkout, so neither needs it. In `edit`, `move`, `archive` and `restore`, which today call `_prepare_write()` first, move it after the lookup and the guard, so the guard is the first thing that can refuse and a refused write cannot upgrade setup or commit. The source kind comes from `stored.branch`: equal to `Repo._main_branch()` is `main`; a name `git.has_local_branch` finds is a local branch; otherwise a remote-tracking branch, split at its first `/` into `<remote>` and `<b>`. `main` in the messages below is that configured name. A write is allowed exactly when the ticket is read from this checkout's working tree (`stored.branch is None`). Otherwise raise `ChittyError` and write nothing:
  - source `main`, from a linked worktree or another checkout: `<ID> is read from main; edit it in the main checkout <path>` (`git.main_checkout`; let its error propagate);
  - source `main`, in the main checkout switched to another branch: `<ID> is read from main; switch this checkout to main first`;
  - source a local ticket branch: `<ID> is in flight on branch <b>; edit it in worktree <path>`, or `...; run git switch <b> first` when no worktree has it;
  - source a remote-tracking branch ahead of a local one: `<ID> is in flight on <remote>/<b>; fast-forward <b> to <remote>/<b> first`; with no local `<b>`: `<ID> is in flight on <remote>/<b>; run git switch --track <remote>/<b> first`.
  - Reads that fail before the guard keep their own errors: diverged branches and a ticket changed on both sides (`TASK-377`), and `no task <ID>` for a ticket not listed.
- Remove `Edit.skip_current_version`, `allow_stale` in `_save`, and every use in `src/chitty/run.py` and the tests (`tests/test_review_trailers.py` has two: rewrite them to assert the refusal).
- The review-with-no-branch handoff in `_run_ticket` (today entered when there is no worktree and no local branch) becomes: if `main_repo.find(id).branch is None`, write `error` on `main` as today; else if `stored.branch` is not the local branch `task-<n>` (a remote-only branch, or a remote ahead of a stale local one), call `main_repo._require_writable(stored)` directly so its error propagates before any agent starts; else carry on as today.
- Out of scope: checking every ticket a `move` or delete will touch before writing (a refusal part-way still leaves earlier files written until `TASK-397` and `TASK-388` land), and the `archive_done` skip (`TASK-397`); docs (`TASK-387`).

Tests: a property with real Git in a new `tests/test_property_ticket_writes.py`, reusing `TASK-393`'s placement and checkout builders from `tests/test_property_ticket_reads.py`. For each placement and checkout kind, `chitty edit <ID> --note x` succeeds exactly where `TASK-393`'s expected result is the working tree, and otherwise fails with that source's message, or with the read error for placements whose read fails. Checkout kinds (4) and (5) are linked worktrees (on `feature`, and detached at `main`), so their message names the main checkout; a separate example switches the main checkout itself to `feature` and expects `switch this checkout to main first`. The test's `chitty.toml` sets `chitty_version` to `CHITTY_VERSION`, so `_prepare_write` writes nothing; one separate example uses a stale `chitty_version`. Expectations come from the placement, not from calling `ticket_source`.

## Acceptance Criteria

- [ ] For every placement and checkout kind, `chitty edit <ID> --note x` succeeds exactly where the ticket is expected from the working tree; every refused edit exits 1 with its source's message (or its read error: `diverged`, changed on both sides, `no task`), changes no file and leaves `HEAD` unchanged; the main-checkout edit of a ticket in flight on `task-<n>` prints the in-flight message (it prints the old message before the change, so the test fails before it)
- [ ] `git grep -nE 'skip_current_version|allow_stale|_require_current_version' -- src tests` prints nothing; `tests/test_review_trailers.py`, `tests/test_run_*.py`, `tests/test_review_merge.py` and `tests/test_landing.py` pass
- [ ] A review run on a ticket with only `origin/task-<n>` (no local branch) fails with `<ID> is in flight on origin/task-<n>; run git switch --track origin/task-<n> first`, starts no agent and writes nothing on `main`; with no branch anywhere it records `error` on `main` as before
- [ ] With a stale `chitty_version` and autocommit on, a refused `chitty edit` of a ticket in flight leaves `HEAD` and `chitty.toml` unchanged (fails before the change); `make check` passes

## Notes

Returned to planning 2026-11-20: the write rule changed (see the Description). Criterion 1 still says writes succeed exactly where the ticket is read from the working tree; that is now wrong for a ticket edited in its own fresh branch worktree.

Split plan 2026-11-22 (overnight planner), since every dependency is now done but the ticket is too large for the worker model: (1) `TASK-547`, the pure message function; (2) this ticket, narrowed to wiring `_require_writable` into the write paths using `write_refusal`, tested over the landed placement matrix (`tests/ticket_placements.py`, kinds 1 to 5) with a mismatch collector as in `tests/test_ticket_placement_reads.py`; (3) a new ticket removing `skip_current_version`/`allow_stale` and the remote-only review handoff (old criteria 2 and 3); (4) a new ticket moving `_prepare_write` after the guard (old criterion 4). Replan (2) after `TASK-547` lands.

Parked with `TASK-547`: see the question in `TASK-547`'s last note.

## History

- 2026-11-18T16:20:16Z lively-quartz-crane → backlog
- 2026-11-18T16:23:23Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:35:59Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:35:59Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:34Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:53:38Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:53:38Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:56:14Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:59:08Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:59:08Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:59:12Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:01:35Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:01:35Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:01:37Z lively-quartz-crane planning → todo
- 2026-11-20T11:15:18Z lively-bronze-crane: changed description, notes
- 2026-11-20T11:15:18Z lively-bronze-crane todo → planning
- 2026-11-21T23:06:25Z lively-zinc-newt: changed dependencies
- 2026-11-22T00:19:39Z lively-zinc-newt: changed dependencies
- 2026-11-22T02:28:48Z lively-zinc-newt: changed dependencies, notes
- 2026-11-22T02:30:04Z lively-zinc-newt: changed labels, notes
