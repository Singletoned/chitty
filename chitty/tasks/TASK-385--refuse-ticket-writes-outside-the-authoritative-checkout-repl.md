---
title: Refuse ticket writes outside the authoritative checkout, replacing the stale-copy guard
status: planning
depends_on:
  - TASK-378
  - TASK-382
  - TASK-383
  - TASK-384
parent: TASK-376
created: 2026-11-18
---

## Description

Today every ticket write runs `Repo._require_current_version` in `src/chitty/store.py`, which refuses when the newest committed copy of the ticket (by commit time, across every ref) is on another branch: `<ID>'s latest committed version is on branch <b>`. Runner handoffs bypass it with `Edit.skip_current_version`. That guard stopped `chitty run --loop` repeatedly on 2026-11-17 (`TASK-343`, `TASK-364`). Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), each ticket is read from one place (`TASK-378`), and writes go only there.

Starts after `TASK-378`, `TASK-382`, `TASK-383` and `TASK-384` land: by then no runner write needs the bypass.

Decisions:

- Replace `_require_current_version(stored)` with `_require_writable(stored)`, called wherever the old guard is: a write is allowed exactly when the ticket is read from this checkout's working tree (`stored.branch is None` after `TASK-378`). Otherwise raise `ChittyError` and write nothing:
  - source `main`: `<ID> is read from main; edit it in the main checkout <path>`, naming the main checkout when `git.main_checkout` finds one, else `on branch main`;
  - source a local ticket branch: `<ID> is in flight on branch <b>; edit it in worktree <path>`, or `...; run git switch <b> first` when no worktree has it;
  - source a remote-tracking branch: `<ID> is in flight on <remote>/<b>; fetch and check out <b> first`.
- Remove `Edit.skip_current_version`, `allow_stale` in `_save`, and every use in `src/chitty/run.py`. The review-with-no-branch handoff writes on `main`, where that ticket is read from the working tree, so it needs no bypass.
- `archive_done` (`chitty archive` with no ID) skips a `done` ticket read from another ref (an unfinished landing, which `_land_pending` finishes) instead of failing the batch, and prints `skipped <ID>: <reason>` for each.
- `move` still refuses when a ticket that references the moved one is read from another ref, now with the new message.
- Out of scope: docs (`TASK-387`).

Tests: a Hypothesis property with real Git in a new `tests/test_property_ticket_writes.py`, inheriting `RepoTestCase` from `tests/support.py`, with `deadline=None` and a small `max_examples` (about 20), reusing the placement generators of `tests/test_property_ticket_reads.py` (`TASK-378`). For each generated placement and checkout (main checkout, or a ticket's linked worktree), try `chitty edit <ID> --note x` on every listed ticket.

## Acceptance Criteria

- [ ] Write property: for generated placements and checkouts, `chitty edit <ID> --note x` succeeds exactly for the tickets `ticket_source` reads from the working tree; every refused edit exits non-zero with the message for its source, changes no file and makes no commit; the main-checkout edit of a ticket in flight on `task-<n>` fails before the change with the old message
- [ ] `Edit` has no `skip_current_version` field, `_require_current_version` and `allow_stale` are gone, and the runner tests in `tests/test_run_*.py`, `tests/test_review_merge.py` and `tests/test_landing.py` pass
- [ ] `chitty archive` with no ID on `main`, with one `done` ticket without a branch and one whose `task-<n>` branch still says `done`, archives the first, prints `skipped <ID>:` for the second, and exits 0; `make check` passes

## History

- 2026-11-18T16:20:16Z lively-quartz-crane → backlog
- 2026-11-18T16:23:23Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:35:59Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:35:59Z lively-quartz-crane backlog → planning
