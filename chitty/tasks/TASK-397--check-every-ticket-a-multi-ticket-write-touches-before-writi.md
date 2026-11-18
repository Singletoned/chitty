---
title: Check every ticket a multi-ticket write touches before writing any
status: cold-read
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

Starts after `TASK-385` lands.

Decisions:

- `move` and `_delete_done` first collect every ticket they will write (the moved or deleted one and each referencing ticket) and run `_require_writable` on each before writing anything. A refusal names the ticket that blocks it.
- `archive_done` skips a `done` ticket read from another ref, in both `move` and `delete` archive modes, and returns `(changes, skipped)`, with `skipped` a list of `(StoredTask, reason)`. The CLI prints `skipped <ID>: <reason>` to stderr for each and `no done tasks to archive` as today when nothing was archived; `--json` prints `{"archived": [...], "skipped": [{"id": ..., "reason": ...}]}`; the MCP `archive` tool returns the same shape. In a linked worktree, `done` tickets read from `main` are skipped too: intended.

Tests: real-Git tests in a new `tests/test_multi_ticket_writes.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`. No property: a fixed set of commands and placements, each in the criteria.

## Acceptance Criteria

- [ ] `chitty move TASK-2 human` in the main checkout, where `TASK-3` (in flight on `task-3`) depends on `TASK-2`, exits 1 naming `TASK-3` and leaves `git status --porcelain` and every ticket file unchanged; the same holds for archiving `TASK-2` in delete mode; both fail before the change
- [ ] `chitty archive` with no ID on `main`, with one `done` ticket without a branch and one whose `task-<n>` branch says `done`, archives the first, prints `skipped <ID>:` to stderr for the second and exits 0, in both archive modes; `--json` and the MCP tool give the `archived`/`skipped` shape; `make check` passes

## History

- 2026-11-18T17:53:36Z lively-quartz-crane → backlog
- 2026-11-18T17:53:40Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T17:53:40Z lively-quartz-crane backlog → planning
- 2026-11-18T17:56:18Z lively-quartz-crane planning → cold-read
