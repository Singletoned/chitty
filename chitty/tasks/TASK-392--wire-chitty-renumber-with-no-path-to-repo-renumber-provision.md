---
title: Wire `chitty renumber` with no path to `Repo.renumber_provisional`
status: cold-read
depends_on:
  - TASK-517
  - TASK-542
  - TASK-543
parent: TASK-376
created: 2026-11-18
---

## Description

`Repo.renumber_provisional()` (`TASK-391`) gives provisional tickets sequential numbers on `main`. Expose it as `chitty renumber` with no path, an idempotent command a person or script can run at any time (decided with the owner: renumbering is cosmetic). Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

`Repo.renumber_provisional()` and `ProvisionalOffMain` (`src/chitty/errors.py`) have landed (rechecked 2026-11-22). Split 2026-11-22 for the worker model: this ticket is the command without `PATH` and its text output; `--json` is `TASK-548`, help text and docs are `TASK-549`, the idempotence property is `TASK-550`. The decisions below cover all four, for reference.

Decisions:

- `PATH` becomes optional on `chitty renumber` in `src/chitty/cli.py`. Without it, call `renumber_provisional()`. With it, behaviour, output and `--json` keys (`renumbered_dict`) are unchanged.
- Every non-error outcome without `PATH` exits 0: renumbered, nothing to renumber, or off `main`. Other errors (duplicate provisional IDs, an unparseable ticket file, an invalid `chitty.toml` on any branch) exit 1 through the usual handler. Outside a Git repository it renumbers, as `TASK-391` treats that as on `main`.
- Without `PATH`: print one `renumbered <old ID> -> <new ID> <path>` line per ticket; with none, print `nothing to renumber`. `renumber_provisional` raises `ProvisionalOffMain`, a `ChittyError` subclass in `src/chitty/errors.py` defined by `TASK-391`, when off `main`; `renumber` catches only that type, prints `provisional tickets are renumbered on main; nothing changed` to stderr and exits 0. Any other `ChittyError` still exits 1 through the usual handler. `nothing to renumber` also goes to stderr, as the idle-queue message does; `renumbered` lines go to stdout, naming the new file's absolute path, as `_report` prints `change.task.path`. With `--json`, stdout carries only the JSON, and both messages still go to stderr.
- `--json` without `PATH` prints a list of `task.as_dict()` items, as `archive` with no ID does (each `moved_from` holds the old ID), and `[]` when there are none, including off `main`, where the message still goes to stderr.
- The MCP `renumber(path)` tool in `src/chitty/mcp.py` is unchanged; no new MCP tool (`tests/test_mcp.py` pins the tool list).
- The first line of `chitty renumber --help` becomes `Renumber provisional tickets on main, or one of several files sharing an ID.`; update `tests/test_renumber.py` `test_help`, which pins the first line. In `docs/plan/cli.md`, describe `renumber` with no `PATH`: the stdout line, the two stderr messages, exit 0, and the `--json` list.

Tests, in `tests/test_renumber_provisional.py`, as a new class inheriting `CliTestCase` from `tests/test_cli.py` (for `run_cli`), with `CHITTY_ACTOR` set as `TestPrepareRenumbering` does. Fixture: set `autocommit = true` in `chitty.toml`, `git init -b main`, set `user.name` and `user.email`, commit; make two provisional tickets with `chitty add` on branch `feature`, then `git switch main` and `git merge feature`. Example tests only (the property is `TASK-550`):

1. On `main`, `chitty renumber` exits 0 and prints one `renumbered <old ID> -> <new ID> <absolute new path>` line per ticket to stdout; a second run prints `nothing to renumber` to stderr.
2. The same outside a Git repository (a temporary directory with no `.git`, `autocommit = false`, provisional files written directly).
3. On `feature`, and on a detached `HEAD`, it prints `provisional tickets are renumbered on main; nothing changed` to stderr, exits 0, and leaves ticket bytes and `git status` unchanged.
4. With an invalid `chitty.toml` on `main`, it exits 1 with the config error.

## Acceptance Criteria

- [ ] Tests 1 and 2 pass and fail on the unchanged code (where `PATH` is required)
- [ ] Tests 3 and 4 pass
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
