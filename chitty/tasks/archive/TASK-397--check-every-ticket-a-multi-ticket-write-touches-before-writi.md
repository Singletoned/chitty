---
title: Check every ticket a multi-ticket write touches before writing any
status: backlog
depends_on:
  - TASK-385
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-385`, a write to a ticket read from another ref is refused. Two multi-ticket writes refuse too late, after writing some files, leaving them changed and uncommitted (a cold read found this in `src/chitty/store.py`):

- `move` runs `_relocate` (writes the new file, unlinks the old) before its loop over referencing tickets calls `_save`, where the guard may refuse one read from another ref;
- `_delete_done` saves referencing tickets in a loop before unlinking, and the guard may refuse a later one.

And `archive_done` (`chitty archive` with no ID) would fail its whole batch on one `done` ticket read from another ref (an unfinished landing, which `_land_pending` finishes).

Starts after `TASK-385` lands (it adds `_require_writable`). "Read from another ref" means `stored.branch is not None`, the predicate `_require_writable` uses.

Decisions:

- `move` and `_delete_done` first collect every ticket they will write (the moved or deleted one and each referencing ticket) and run `_require_writable` on each before writing anything. A refusal names the ticket that blocks it.
- `archive_done` skips a `done` ticket when it, or (in delete mode) any ticket deleting it would rewrite, is read from another ref. It decides every skip before writing any file. This holds in both `move` and `delete` archive modes. It and returns `(changes, skipped)`, with `skipped` a list of `(StoredTask, reason)`. The CLI prints `skipped <ID>: <reason>` to stderr for each (also with `--json`), and `no done tasks to archive` on stdout as today when nothing was archived, even if some were skipped; `--json` prints `{"archived": [...], "skipped": [{"id": "TASK-5", "reason": "..."}]}` with string IDs; the MCP `archive` tool returns the same shape. Rewrite the two tests that expect a list: `tests/test_cli.py` around line 2011 and `tests/test_mcp.py` around lines 160-162. In a linked worktree, `done` tickets read from `main` are skipped too: intended.

Tests: tickets that must be deleted are first made `done` through `review`. Real-Git tests in a new `tests/test_multi_ticket_writes.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`. No property: a fixed set of commands and placements, each in the criteria.

## Acceptance Criteria

- [ ] `chitty move TASK-2 human` in the main checkout, where `TASK-3` (in flight on `task-3`) depends on `TASK-2`, exits 1 naming `TASK-3` and leaves `git status --porcelain` and every ticket file unchanged; the same holds for archiving `TASK-2` in delete mode; both fail before the change
- [ ] `chitty archive` with no ID on `main`, with one `done` ticket without a branch and one whose `task-<n>` branch says `done`, archives (or, in delete mode, deletes) the first, prints `skipped <ID>:` to stderr for the second and exits 0, in both archive modes
- [ ] In delete mode, a `done` `TASK-1` on `main` referenced by `TASK-2` in flight on `task-2` is skipped by `chitty archive` with no ID, while another unreferenced `done` ticket is deleted, and no file is left changed and uncommitted; this fails before the change
- [ ] `--json` and the MCP tool give the `archived`/`skipped` shape, the two rewritten tests pass, and `make check` passes

## Notes

Superseded, 2026-11-23: built on `TASK-385`'s write refusal, which the person dropped this morning (recorded in `TASK-602`): Chitty does not refuse ticket writes because another branch has a different or newer copy; it writes the current checkout's copy and warns. Parked in `backlog` until `TASK-602` is planned; then archive it or rewrite it against `TASK-602`.

## History

- 2026-11-18T17:53:36Z lively-quartz-crane → backlog
- 2026-11-18T17:53:40Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:53:40Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:18Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:00:38Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:00:38Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:00:40Z lively-quartz-crane planning → todo
- 2026-11-23T16:07:39Z youthful-quartz-zander: changed notes
- 2026-11-23T16:07:39Z youthful-quartz-zander todo → backlog
- 2026-11-23T16:41:26Z youthful-quartz-zander backlog → archived
