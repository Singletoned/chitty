---
title: Keep `chitty fix` to ticket files read from this checkout
status: planning
depends_on:
  - TASK-378
  - TASK-398
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-378`, a ticket in flight is read from its branch, but `chitty fix` (`fix` in `src/chitty/check.py`) still scans and rewrites this checkout's ticket files. In the main checkout it can rewrite `main`'s stale copy of an in-flight ticket, a write on `main` for a ticket with a branch, which the new model forbids (`docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`) and which `TASK-377` then reports as changed on both sides.

Starts after `TASK-378` and `TASK-398` (which gives `fix` its `paths: Sequence[Path] | None` signature) land.

Decisions:

- `fix` (which scans files with `scan`, not `Repo`) builds a map from resolved path to `StoredTask` once from `Repo.tasks` over every context, keyed by `StoredTask.path.resolve()`. It repairs a scanned file only when the map has it with `branch is None`. Any other file (read from another ref, or absent from the map, for example `main`'s copy of a ticket whose slug changed on its branch) is not repaired and is reported as a warning `Problem(path, "skipped: read from <ref>", "warning")`, or `"skipped: not the ticket's authoritative copy"` when absent; `errors()` ignores warnings and the CLI already prints problems. In a ticket worktree this also skips tickets read from `main`: intended.
- Errors from `Repo.tasks` (diverged branches, a ticket changed on both sides) propagate; never catch them in the existing `except ChittyError: continue`. A diverged ticket therefore stops `fix`, loudly, as decided.
- `chitty check` keeps checking every file in this checkout, as a file-format check.

Tests: real-Git tests in a new `tests/test_fix_sources.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`. The fixable defect is a lower-case reference, `depends_on: [task-3]`, which `fix` rewrites to `TASK-3`; `main`'s copy of an in-flight ticket is committed directly with Git. No property: a fixed set of file sources, each in the criteria.

## Acceptance Criteria

- [ ] In the main checkout, with `TASK-5` in flight on `task-5` (ahead of `main`) and `main`'s copy of its file holding `depends_on: [task-3]`, `chitty fix` leaves that file byte-identical, prints a `skipped: read from task-5` warning and makes no commit (fails before the change); the same defect in a ticket with no branch is rewritten to `TASK-3` (passes before and after)
- [ ] In the linked worktree of `task-5`, `chitty fix` repairs `TASK-5`'s own file and skips `main`'s tickets with warnings; with local `task-7` and `origin/task-7` diverged, `chitty fix` exits 1 naming both; `make check` passes

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
