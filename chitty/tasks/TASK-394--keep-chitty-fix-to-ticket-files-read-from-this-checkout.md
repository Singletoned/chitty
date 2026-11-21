---
title: Keep `chitty fix` to ticket files read from this checkout
status: doing
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-378`, a ticket in flight is read from its branch, but `chitty fix` (`fix` in `src/chitty/check.py`) still scans and rewrites this checkout's ticket files. In the main checkout it can rewrite `main`'s stale copy of an in-flight ticket, a write on `main` for a ticket with a branch, which the new model forbids (`docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`) and which `TASK-377` then reports as changed on both sides.

Starts after `TASK-378` lands.

Decisions:

- New `Repo.source_of(task_id) -> str | None` (in `src/chitty/store.py`, beside `TASK-378`'s map): the `ticket_source` result for that ID, as a short ref name, or `None` for the working tree, computed from filenames and refs; a copy that fails to parse is treated as not provisional, so a malformed file never stops it. Errors from `ticket_source` (diverged branches, a ticket changed on both sides) propagate.
- `fix` (which scans files with `scan`, not `Repo`) asks `source_of` for each scanned file's ID (from its filename), only for files inside the `paths` filter and after `scan` accepts the name, before parsing its content. It repairs the file only when `source_of` is `None` and the file is the one `Repo.find(id).path` resolves to; a second working-tree file with the same ID is skipped with the warning, and `check` keeps reporting the duplicate. Files that fail to scan or parse are left to the existing repair loop and to `check`, exactly as today (`tests/test_check.py` `test_fix_reports_unresolved_problems_without_writing` must still pass). Any other file (read from another ref, or absent from the map, for example `main`'s copy of a ticket whose slug changed on its branch) is not repaired and is reported as a warning `Problem(path, "skipped: read from <ref>", "warning")` in `fix`'s problems list (the second element it returns), only for files within the `paths` filter; `errors()` ignores warnings and the CLI already prints problems. In a ticket worktree this also skips tickets read from `main`: intended.
- Errors from `source_of` propagate; never catch them in the existing `except ChittyError: continue`. A diverged ticket therefore stops `fix`, loudly, as decided. Relies on `TASK-378`'s contract that a working-tree read has `branch is None`, including on the ticket's own branch.
- `chitty check` keeps checking every file in this checkout, as a file-format check.

Tests: real-Git tests in a new `tests/test_fix_sources.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`. The fixable defect is a lower-case reference, `depends_on: [task-3]`, which `fix` rewrites to `TASK-3`; `main`'s copy of an in-flight ticket is committed directly with Git. No property: a fixed set of file sources, each in the criteria.

## Acceptance Criteria

- [ ] In the main checkout, with `main`'s copy of `TASK-5` holding `depends_on: [task-3]` committed before `task-5` is created, and `task-5` then getting its own commit changing only another file (so `main`'s copy is unchanged since the split and the branch is ahead), `chitty fix` leaves `main`'s file byte-identical, lists a `skipped: read from task-5` warning and leaves `HEAD` unchanged (fails before the change); the same defect in a ticket with no branch is rewritten to `TASK-3` (passes before and after)
- [ ] In the linked worktree of `task-5`, where `task-5` has a commit ahead of `main` changing `TASK-5` and the worktree's `TASK-5` file holds the lower-case defect, `chitty fix` repairs that file and lists `skipped: read from main` warnings for `main`'s tickets; with a malformed ticket file present, `chitty fix` still repairs the others and reports it as today
- [ ] In the main checkout, with local `task-7` and `origin/task-7` (made by `git update-ref`) at sibling commits, both ahead of `main` and each changing `TASK-7`, `chitty fix` exits 1 naming both; `make check` passes

## History

- 2026-11-18T16:38:05Z lively-quartz-crane → backlog
- 2026-11-18T16:39:35Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:35Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:51:22Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:51:22Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:51:24Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:55:48Z lively-quartz-crane: changed title, dependencies, description, acceptance criteria
- 2026-11-18T17:55:48Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:56:16Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:58:19Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:59:10Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:59:10Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:59:14Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:00:54Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:00:54Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:00:56Z lively-quartz-crane planning → todo
- 2026-11-21T13:05:19Z brisk-hazel-crane todo → doing
