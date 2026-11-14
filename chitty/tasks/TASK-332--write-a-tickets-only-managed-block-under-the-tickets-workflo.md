---
title: Write a tickets-only managed block under the tickets workflow
status: planning
depends_on:
  - TASK-330
created: 2026-11-14
---

## Description

Under `workflow = "tickets"` (the resolved `config.workflow` from TASK-330), the managed Chitty block holds only the ticketing rules.

- Split `src/chitty/guide.md` into two package files: `guide.md` keeps its first paragraph (the `## Chitty` heading through the `chitty --help` line), and a new `src/chitty/guide-runner.md` holds the rest. Each rule exists in one file only.
- Add `managed_guide(workflow: str) -> str` in `src/chitty/store.py`: `"tickets"` returns `guide.md`; `"runner"` returns `guide.md`, a blank line, then `guide-runner.md`, byte-identical to today's `guide.md`. Any other value raises `ChittyError`.
- Callers that print or install the block pass the repository's workflow: `_managed_agents` in `store.py` (what `chitty init` writes into `AGENTS.md`), `chitty guide` with no role in `cli.py`, the MCP `chitty://guide` resource and the MCP server `instructions` in `mcp.py`, and the `## Chitty` text written by `src/chitty/import_backlog.py`. Outside a Chitty repository, and wherever no config is found, use `"runner"`. Build the MCP server's instructions when `chitty mcp` starts, from the config of the directory it starts in, not at import time.
- `chitty init` already replaces a block whose text differs, so changing the workflow and re-running it swaps the block; no new code should be needed for that, but test it.
- Role guides (`chitty guide work` and so on) are unchanged here; TASK-334 hides them.
- No property test: the output is fixed text chosen from a set of two workflows, each tested. Tests go in `tests/test_guide_workflow_block.py`.

## Acceptance Criteria

- [ ] `managed_guide("runner")` equals the `guide.md` text at the commit before this change (read it with `git show`, or embed it in the test), and `managed_guide("tickets")` is that text up to and including the `chitty --help` line; `managed_guide("other")` raises `ChittyError`. The tickets case fails today.
- [ ] In a temp repository with `workflow = "tickets"`, `chitty init` writes the tickets block into `AGENTS.md`, `chitty guide` prints it, and the MCP `chitty://guide` resource and server instructions return it; with `workflow = "runner"`, and outside any repository, all of them give the runner block.
- [ ] Changing `workflow` from `runner` to `tickets` and re-running `chitty init` replaces the block in `AGENTS.md`, leaving text outside the markers unchanged; and the reverse.
- [ ] No sentence of the tickets block appears in `guide-runner.md`; `make check` passes.

## History

- 2026-11-14T18:21:55Z friendly-ginger-adder → planning
- 2026-11-14T18:23:28Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:29:47Z friendly-ginger-adder: changed description, acceptance criteria
