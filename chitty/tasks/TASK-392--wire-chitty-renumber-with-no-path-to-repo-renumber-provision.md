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
- Without `PATH`: print one `renumbered <old ID> -> <new ID> <path>` line per ticket; with none, print `nothing to renumber`. When `renumber_provisional` raises its off-`main` error, print `provisional tickets are renumbered on main; nothing changed` and exit 0. Any other error exits non-zero as usual.
- `--json` without `PATH` prints a list of renumbered tickets, as `archive` with no ID does, and `[]` when there are none.
- The MCP `renumber(path)` tool in `src/chitty/mcp.py` is unchanged; no new MCP tool (`tests/test_mcp.py` pins the tool list).
- Update the `renumber` help text and `docs/plan/cli.md`; update `tests/test_renumber.py` `test_help`, which pins the current first help line.

Tests: CLI tests in `tests/test_renumber_provisional.py` (`TASK-391`'s file). No property: thin CLI wiring over a fixed set of outcomes, each in the criteria.

## Acceptance Criteria

- [ ] On `main` with two provisional tickets, `chitty renumber` prints one `renumbered` line each and exits 0; run again it prints `nothing to renumber`; on a branch it prints `provisional tickets are renumbered on main; nothing changed` and exits 0; the first fails before the change
- [ ] `chitty renumber --json` prints a list (`[]` when nothing changes); `chitty renumber PATH` for two files sharing an ID, its `--json`, and the MCP `renumber` tool behave as before; `make check` passes

## History

- 2026-11-18T16:37:33Z lively-quartz-crane → backlog
- 2026-11-18T16:37:39Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:37:39Z lively-quartz-crane backlog → planning
