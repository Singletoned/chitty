---
title: Refuse ticket writes outside the authoritative checkout, replacing the stale-copy guard
status: cold-read
depends_on:
  - TASK-378
  - TASK-382
  - TASK-383
  - TASK-384
  - TASK-393
parent: TASK-376
created: 2026-11-18
---

## Description

Today every ticket write runs `Repo._require_current_version` in `src/chitty/store.py`, which refuses when the newest committed copy of the ticket (by commit time, across every ref) is on another branch: `<ID>'s latest committed version is on branch <b>`. Runner handoffs bypass it with `Edit.skip_current_version`. That guard stopped `chitty run --loop` repeatedly on 2026-11-17 (`TASK-343`, `TASK-364`). Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), each ticket is read from one place (`TASK-378`), and writes go only there.

Starts after `TASK-378`, `TASK-382`, `TASK-383`, `TASK-384` and `TASK-393` (whose placement builders the test reuses) land: by then no runner write needs the bypass.

Decisions:

- Replace `_require_current_version(stored)` with `_require_writable(stored)`, called wherever the old guard is: `edit`'s review gate (its condition loses the `skip_current_version` clause), `_set_archived` (so `archive` and `restore`), `_delete_done`, `move` and `_save`. `add` creates a new file, and `renumber PATH` works on duplicate files in this checkout, so neither needs it. `renumber_provisional` (`TASK-391`, in either order) skips files read from another ref instead. In each write the guard runs before `_prepare_write`, so a refused write cannot upgrade setup or commit. A write is allowed exactly when the ticket is read from this checkout's working tree (`stored.branch is None`). Otherwise raise `ChittyError` and write nothing:
  - source `main`, from a linked worktree or another checkout: `<ID> is read from main; edit it in the main checkout <path>` (`git.main_checkout`; let its error propagate);
  - source `main`, in the main checkout switched to another branch: `<ID> is read from main; switch this checkout to main first`;
  - source a local ticket branch: `<ID> is in flight on branch <b>; edit it in worktree <path>`, or `...; run git switch <b> first` when no worktree has it;
  - source a remote-tracking branch ahead of a local one: `<ID> is in flight on <remote>/<b>; fast-forward <b> to <remote>/<b> first`; with no local `<b>`: `<ID> is in flight on <remote>/<b>; run git switch --track <remote>/<b> first`.
  - Reads that fail before the guard keep their own errors: diverged branches and a ticket changed on both sides (`TASK-377`), and `no task <ID>` for a ticket not listed.
- Remove `Edit.skip_current_version`, `allow_stale` in `_save`, and every use in `src/chitty/run.py` and the tests (`tests/test_review_trailers.py` has two; rewrite them to assert the refusal or drop the bypass).
- The review-with-no-branch handoff in `_run_ticket` (today entered when there is no worktree and no local branch) becomes: if `main_repo.find(id).branch is None`, write `error` on `main` as today; else if there is no local branch (a remote-only branch), call `main_repo._require_writable(stored)` directly so its error propagates; else carry on as today.
- Out of scope: checking every ticket a `move` or delete will touch before writing, and the `archive_done` skip (`TASK-397`); docs (`TASK-387`).

Tests: a property with real Git in a new `tests/test_property_ticket_writes.py`, reusing `TASK-393`'s placement and checkout builders from `tests/test_property_ticket_reads.py`. For each placement and checkout kind, `chitty edit <ID> --note x` succeeds exactly where `TASK-393`'s expected result is the working tree, and otherwise fails with that source's message, or with the read error for placements whose read fails. Checkout kinds (4) and (5) are linked worktrees (on `feature`, and detached at `main`), so their message names the main checkout; a separate example switches the main checkout itself to `feature` and expects `switch this checkout to main first`. The repository's setup is current, so `_prepare_write` writes nothing. Expectations come from the placement, not from calling `ticket_source`.

## Acceptance Criteria

- [ ] For every placement and checkout kind, `chitty edit <ID> --note x` succeeds exactly where the ticket is expected from the working tree; every refused edit exits 1 with its source's message (or its read error: `diverged`, changed on both sides, `no task`), changes no file and leaves `HEAD` unchanged; the main-checkout edit of a ticket in flight on `task-<n>` prints the in-flight message (it prints the old message before the change, so the test fails before it)
- [ ] `git grep -nE 'skip_current_version|allow_stale|_require_current_version' -- src tests` prints nothing; `tests/test_review_trailers.py`, `tests/test_run_*.py`, `tests/test_review_merge.py` and `tests/test_landing.py` pass
- [ ] A review run on a ticket with only `origin/task-<n>` (no local branch) fails with the guard's message and writes nothing on `main`; with no branch anywhere it records `error` on `main` as before; `make check` passes

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
