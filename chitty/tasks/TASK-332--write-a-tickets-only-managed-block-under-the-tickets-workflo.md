---
title: Write a tickets-only managed block under the tickets workflow
status: doing
depends_on:
  - TASK-330
created: 2026-11-14
---

## Description

Under `workflow = "tickets"` (the resolved `config.workflow` from TASK-330), the managed Chitty block holds only the ticketing rules.

- Split `src/chitty/guide.md` into two package files: `guide.md` keeps its first paragraph (the `## Chitty` heading through the `chitty --help` line), and a new `src/chitty/guide-runner.md` holds the rest. Each rule exists in one file only.
- Add to `src/chitty/store.py`:
  - `managed_guide(workflow: str) -> str`: `"tickets"` returns `guide.md`; `"runner"` returns `guide.md`, a blank line, then `guide-runner.md`, byte-identical to today's `guide.md`. Any other value raises `ChittyError`.
  - `repository_guide(start_dir: Path) -> str`: `managed_guide` of the workflow in the config found from `start_dir`, or of `"runner"` when no config is found. Config errors, including an invalid `workflow`, raise as they do elsewhere.
  - `guide(role, ticket_id)` now always takes a role; the general text comes only from these two functions. Update its existing callers and the tests that call `guide()` with no role.
- Callers that print or install the block use the repository's workflow: `_managed_agents` (what `chitty init` writes into `AGENTS.md`; `init_repo` must load the config before writing the block, but keep validating the existing guide markers before any file is written), `chitty guide` with no role in `cli.py`, the `## Chitty` text written by `src/chitty/import_backlog.py` (its caller has `repo.config`), and MCP.
- MCP (`src/chitty/mcp.py`): replace the module-level server with `create_server(start_dir: Path) -> MCPServer`, which builds the server with `instructions=repository_guide(start_dir)` and registers the `chitty://guide` resource and every tool on it. `chitty mcp` calls it with the current directory. Use no private attributes of the MCP library. TASK-333 will register the `next` tool conditionally in the same factory.
- Tests whose result depends on the workflow set `workflow` explicitly and never rely on the default, which changes with the version; TASK-335 pins the shared `tests/support.py` config. A fresh `chitty init` config has no `workflow` line until TASK-331, so it resolves by version; that is out of scope here. Role guides (`chitty guide work` and so on) are unchanged here; TASK-334 hides them.
- No property test: the output is fixed text chosen from a set of two workflows, each tested. Tests go in `tests/test_guide_workflow_block.py`.

## Acceptance Criteria

- [ ] `managed_guide("runner")` equals the `guide.md` text at the commit before this change (read it with `git show`, or embed it in the test), and `managed_guide("tickets")` is that text up to and including the `chitty --help` line; `managed_guide("other")` raises `ChittyError`. The tickets case fails today.
- [ ] In a temp repository with `workflow = "tickets"`, `chitty init` writes the tickets block into `AGENTS.md`, `chitty guide` prints it, the import in `src/chitty/import_backlog.py` writes it, and a server from `create_server` returns it as its instructions and its `chitty://guide` resource; with `workflow = "runner"` all four give the runner block, and outside any repository `chitty guide` and `create_server` give the runner block.
- [ ] In a temp repository, changing an explicit `workflow` line from `runner` to `tickets` and re-running `chitty init` replaces the block in `AGENTS.md`, leaving text outside the markers unchanged; and the reverse. Existing tests for damaged guide markers still pass, with no file written before that error.
- [ ] No sentence of the body of `guide.md` (the text after its `## Chitty` heading) appears in `guide-runner.md`; `src/chitty/mcp.py` imports no name starting with `_` from the `mcp` package and reads no such attribute of its objects; `make check` passes.

## Notes

Cold read starting point: `refs/cold-read/TASK-332/2` (a Haiku implementing read on top of TASK-330's read; `make check` green; mutants M1 to M5 killed). Its files: `src/chitty/guide.md`, `src/chitty/guide-runner.md`, `src/chitty/store.py`, `src/chitty/cli.py`, `src/chitty/import_backlog.py`, `src/chitty/mcp.py`, `tests/test_guide_workflow_block.py`, `tests/fixtures/guide-before-workflow.md`, and one-token call-site swaps in `tests/test_cli.py`, `tests/test_mcp.py`, `tests/test_next.py`, `tests/test_renumber.py`, `tests/test_statuses_planning.py`, `tests/test_guide_backticks.py`, `tests/test_guide_literal_star.py`. See them with `git show refs/cold-read/TASK-332/2:<path>`. Rebase onto the real TASK-330 on `main`; check against the current criteria rather than trusting it.

## History

- 2026-11-14T18:21:55Z friendly-ginger-adder → planning
- 2026-11-14T18:23:28Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:29:47Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:37:24Z friendly-ginger-adder: changed owner
- 2026-11-14T18:37:24Z friendly-ginger-adder planning → cold-read
- 2026-11-14T18:46:21Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:46:21Z friendly-ginger-adder cold-read → planning
- 2026-11-14T18:46:37Z friendly-ginger-adder planning → cold-read
- 2026-11-14T18:56:10Z friendly-ginger-adder: changed description, acceptance criteria, notes
- 2026-11-14T18:56:10Z friendly-ginger-adder cold-read → planning
- 2026-11-14T18:56:12Z friendly-ginger-adder: changed owner
- 2026-11-14T18:56:12Z friendly-ginger-adder planning → todo
- 2026-11-14T20:01:11Z vivid-pearl-urchin todo → doing
