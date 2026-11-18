---
title: Wire `chitty renumber` with no path to `Repo.renumber_provisional`
status: planning
depends_on:
  - TASK-391
parent: TASK-376
created: 2026-11-18
---

## Description

`Repo.renumber_provisional()` (`TASK-391`) gives provisional tickets sequential numbers on `main`. Expose it as `chitty renumber` with no path, an idempotent command a person or script can run at any time (decided with the owner: renumbering is cosmetic). Context: `docs/plan/ticket-state.md`, "Planning decisions" (on branch `plan/ticket-state` until it lands on `main`).

Starts after `TASK-391` lands.

Decisions:

- `PATH` becomes optional on `chitty renumber` in `src/chitty/cli.py`. Without it, call `renumber_provisional()`. With it, behaviour, output and `--json` keys (`renumbered_dict`) are unchanged.
- Without `PATH`: print one `renumbered <old ID> -> <new ID> <path>` line per ticket; with none, print `nothing to renumber`. `renumber_provisional` raises `ProvisionalOffMain`, a `ChittyError` subclass in `src/chitty/errors.py` defined by `TASK-391`, when off `main`; `renumber` catches only that type, prints `provisional tickets are renumbered on main; nothing changed` to stderr and exits 0. Any other `ChittyError` still exits 1 through the usual handler. `nothing to renumber` also goes to stderr, as the idle-queue message does; `renumbered` lines go to stdout, naming the new file's path.
- `--json` without `PATH` prints a list of `task.as_dict()` items, as `archive` with no ID does (each `moved_from` holds the old ID), and `[]` when there are none, including off `main`, where the message still goes to stderr.
- The MCP `renumber(path)` tool in `src/chitty/mcp.py` is unchanged; no new MCP tool (`tests/test_mcp.py` pins the tool list).
- Update the `renumber` help text and `docs/plan/cli.md`; update `tests/test_renumber.py` `test_help`, which pins the current first help line.

Tests: CLI tests in `tests/test_renumber_provisional.py` (`TASK-391`'s file). Make provisional tickets with `chitty add` on branch `feature` of a `git init -b main` repository, then `git switch main` and `git merge feature`. A Hypothesis property for idempotence: for 0 to 3 provisional tickets (small `max_examples`, `deadline=None`), the first run prints exactly that many `renumbered` lines and the second prints `nothing to renumber` and leaves every file byte-identical.

## Acceptance Criteria

- [ ] Idempotence property passes; with two provisional tickets on `main`, the first `chitty renumber` prints one `renumbered <old ID> -> <new ID> <new path>` line each to stdout and exits 0; this fails before the change
- [ ] On `feature`, and on a detached `HEAD`, `chitty renumber` prints `provisional tickets are renumbered on main; nothing changed` to stderr, exits 0 and changes nothing; another `ChittyError` (an invalid `chitty.toml`) exits 1 with its message
- [ ] `chitty renumber --json` with two provisional tickets lists both, each with its new ID and `moved_from` the old one; it prints `[]` when nothing changes and off `main`
- [ ] `tests/test_renumber.py` (except `test_help`, updated to the new first help line) and `tests/test_mcp.py` `test_tools_mirror_the_cli` pass unchanged; `docs/plan/cli.md` describes `renumber` with no path; `make check` passes

## History

- 2026-11-18T16:37:33Z lively-quartz-crane → backlog
- 2026-11-18T16:37:39Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:37:39Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:40Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:42:17Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:42:17Z lively-quartz-crane cold-read → planning
