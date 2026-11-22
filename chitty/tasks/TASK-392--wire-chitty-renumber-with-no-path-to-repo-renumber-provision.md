---
title: Wire `chitty renumber` with no path to `Repo.renumber_provisional`
status: todo
depends_on:
  - TASK-517
  - TASK-542
  - TASK-543
parent: TASK-376
created: 2026-11-18
---

## Description

`Repo.renumber_provisional()` gives provisional tickets sequential numbers on `main` (`TASK-517`, landed). Expose it as `chitty renumber` with no `PATH`, a command a person or script can run at any time (decided with the owner: renumbering is cosmetic). `ProvisionalOffMain` (`src/chitty/errors.py`) is raised off `main`. Rechecked on `main` 2026-11-22. Split for the worker model: `--json` is `TASK-548`, help text and docs `TASK-549`, the idempotence property `TASK-550`.

Decisions for this ticket:

- In `src/chitty/cli.py`, make `PATH` optional on `renumber` (today `path` is a required argument). With `PATH`, behaviour and output are unchanged.
- Without `PATH`, call `_repo().renumber_provisional()`:
  - For each returned `Change`, print `renumbered <old ID> -> <new ID> <absolute new path>` to stdout, where the old ID is `change.task.task.frontmatter.moved_from` and the path is `change.task.path`. No actor suffix (unlike `_report`).
  - If it returns `()`, print `nothing to renumber` to stderr. Exit 0.
  - Catch `ProvisionalOffMain` only: print `provisional tickets are renumbered on main; nothing changed` to stderr and exit 0. Every other `ChittyError` exits 1 through the usual handler (`_Group.invoke`).
- Outside a Git repository it renumbers.

Tests, in `tests/test_renumber_provisional.py`, as a new class inheriting `CliTestCase` from `tests/test_cli.py`, with `CHITTY_ACTOR` set as `TestPrepareRenumbering` does. Git fixture: set `autocommit = true` in `chitty.toml`, `git init -b main`, set `user.name` and `user.email`, commit; `git switch -c feature`; `chitty add "One" -d "Fixture."` and `chitty add "Two" -d "Fixture."` (on a branch these get provisional IDs); `git switch main`; `git merge feature`.

1. On `main`, `chitty renumber` exits 0 and prints exactly two `renumbered <old ID> -> TASK-<n> <path>` lines to stdout; a second run prints `nothing to renumber` to stderr.
2. Outside Git: a temporary directory with no `.git`, `CONFIG` from `tests/support.py` (`autocommit = false`), and two provisional files written with the `put()` helper in `TestPrepareRenumbering`; `chitty renumber` prints two `renumbered` lines and exits 0.
3. On `feature`, and on a detached `HEAD`, it exits 0, stderr is exactly `provisional tickets are renumbered on main; nothing changed`, and ticket bytes and `git status --porcelain` are unchanged.
4. With an invalid `chitty.toml` (for example a line `bad = [`) on `main`, it exits 1 and stderr contains `invalid TOML`.

All four fail on today's code (a cold reader's probe: `Error: Missing argument 'PATH'`, exit 2); because each asserts its exact message, a usage error cannot pass them.

## Acceptance Criteria

- [ ] Tests 1 and 2 pass, and each fails on today's code
- [ ] Tests 3 and 4 pass, and each fails on today's code
- [ ] `tests/test_renumber.py` (except `test_help`, which `TASK-549` changes) and `tests/test_mcp.py` `test_tools_mirror_the_cli` pass; `make check` passes

## Notes

The store method moved to `TASK-517`, which depends on the preflight `TASK-391`. Update this ticket against the landed store behavior and cold-read it before moving it back to `todo`.

## History

- 2026-11-18T16:37:33Z lively-quartz-crane → backlog
- 2026-11-18T16:37:39Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:37:39Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:40Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:42:17Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:42:17Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:44:51Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:46:21Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:46:21Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:48:26Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:49:45Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:49:45Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:49:47Z lively-quartz-crane planning → todo
- 2026-11-21T18:37:19Z eager-ginger-adder: changed dependencies, notes
- 2026-11-21T18:37:19Z eager-ginger-adder todo → planning
- 2026-11-22T01:35:37Z lively-zinc-newt: changed dependencies
- 2026-11-22T03:22:42Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:22:42Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:25:13Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:25:13Z lively-zinc-newt cold-read → todo
