---
title: Hide run and next under the tickets workflow
status: review
labels:
  - needs-minor
depends_on:
  - TASK-330
  - TASK-332
created: 2026-11-14
---

## Description

Under `workflow = "tickets"` (the resolved `config.workflow` from TASK-330), hide the runner commands `run` and `next`.

- CLI (`src/chitty/cli.py`): when the current directory is in a Chitty repository whose config loads with workflow `tickets`, `chitty --help` does not list `run` or `next`. Invoking either exits 1 with `chitty <command> needs workflow = "runner" in the Chitty config` on stderr, not click's "No such command". A custom `click.Group` overriding `list_commands` and `get_command` is one way.
- When no config is found, or it fails to load, `--help` lists every command, so help still works while diagnosing a broken config; running `run` or `next` then reports the config error as today.
- MCP (`src/chitty/mcp.py`): in `create_server(start_dir)` (added by TASK-332), register the `next` tool only when the workflow of the config found from `start_dir` is `runner`, or when no config is found. Under `tickets`, the tool list has no `next`.
- Under `runner`, and outside a repository, nothing changes. Under `tickets`, the refusal comes before the setup-version check. An existing test whose config has no `workflow` line and a recorded version of `0.5.0` or later (such as `test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty` in `tests/test_next.py`, which records `99.0.0`) now resolves to `tickets`: add `workflow = "runner"` to that test's config rather than changing the behaviour.
- A broken config still makes `create_server` raise, as it does today.
- Keep the check in one place in `store.py` or `config.py` (for example `require_runner(config, command)`), so the CLI and MCP cannot diverge.
- No property test: a small fixed set (two workflows, plus no repository, times two commands), each case tested. Tests go in `tests/test_workflow_commands.py`, and set `workflow` explicitly in every config they write.

## Acceptance Criteria

- [x] In a temp repository with `workflow = "tickets"`, `chitty --help` lists neither `run` nor `next` but still lists `list` and `add`; `chitty run` and `chitty next` each exit 1 with the message naming the command and `workflow = "runner"`. Both fail today.
- [x] With `workflow = "runner"`, and in a directory with no Chitty config, `chitty --help` lists `run` and `next` and both commands behave as before; `tests/test_next.py` passes, changed only by adding `workflow = "runner"` to configs that would otherwise resolve to `tickets`. With a config that fails to load, `chitty --help` lists every command and `chitty next` reports the config error.
- [x] An MCP server started in a `tickets` repository lists no `next` tool, and one started in a `runner` repository lists it; use the existing pattern in `tests/test_mcp.py`. `make check` passes.

## Plan

Use the shared configured workflow lookup and runner guard for CLI and MCP. Add focused tests for tickets, runner, absent config, and broken config behavior; explicitly set workflow in test configs that rely on runner commands. Verify the regression tests fail before implementation, then run format and full checks.

## Notes

Cold read starting point: `refs/cold-read/TASK-333/1` (on top of TASK-332's read; mutants M1 to M5 killed). Its files: `src/chitty/config.py` (`configured_workflow`), `src/chitty/cli.py` (a `click.Group` subclass), `src/chitty/mcp.py`, `tests/test_workflow_commands.py`; see them with `git show refs/cold-read/TASK-333/1:<path>`. It did not yet fix `test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty`, which needs `workflow = "runner"`. Check it against the current criteria rather than trusting it.

Added CLI visibility/refusal and MCP tool filtering using shared config workflow lookup; added explicit runner workflow to the run regression fixture. `make check` passed (584 Python tests and Node tests). Note: focused tests were first run after implementation, not against the unfixed behavior.

Review failed (tests): Add coverage for the missing command cases and make the tickets refusal apply before Click parses command options. These are newly discovered findings; there are no earlier review failures.
1: fail - A throwaway CliRunner invocation in a tickets repository printed exit 2 and `No such option` for `next --json` and `run --mode work`; `run --help` printed exit 0 and generic help. All invocations must instead exit 1 with the required workflow message. Bare-command tests pass and fail against main, but do not cover arguments.
2: fail - `tests/test_workflow_commands.py` checks only help outside a repository, not execution of both `run` and `next` there; it also does not execute both commands with an explicitly configured runner workflow. Add the requested fixed cases. `make check` passed 584 Python tests and Node tests; broken-config next reports invalid TOML.
3: pass - `make format && make check` passed, including MCP workflow tests. Running `tests.test_workflow_commands` with main source via PYTHONPATH failed `test_mcp_next_follows_workflow` because tickets still listed `next`, demonstrating regression coverage.

Fixed tickets workflow refusals to raise during command resolution, before Click parses options or handles --help. Expanded tests for argument/help invocations and command execution in runner and no-config contexts. Verified: focused workflow tests and make format && make check pass (584 Python tests and Node tests). The requested regression test was not run before the fix in this revision; prior review evidence reports the original defect. No follow-ups.

## Summary

Implemented and committed as f2b6bb9 (Task: TASK-333). Tickets workflow commands now refuse before option parsing, with coverage for arguments and --help. Verified with focused workflow tests and make format && make check (584 Python tests and Node tests). No follow-ups.

## History

- 2026-11-14T18:21:57Z friendly-ginger-adder → planning
- 2026-11-14T18:23:30Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:29:48Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:29:59Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:47:00Z friendly-ginger-adder: changed description
- 2026-11-14T18:56:15Z friendly-ginger-adder: changed owner
- 2026-11-14T18:56:15Z friendly-ginger-adder planning → cold-read
- 2026-11-14T19:21:54Z friendly-ginger-adder: changed description, acceptance criteria, notes
- 2026-11-14T19:21:54Z friendly-ginger-adder cold-read → planning
- 2026-11-14T19:21:57Z friendly-ginger-adder: changed owner
- 2026-11-14T19:21:57Z friendly-ginger-adder planning → todo
- 2026-11-14T20:18:54Z jolly-indigo-vole todo → doing
- 2026-11-14T20:19:07Z jolly-indigo-vole: wrote the plan
- 2026-11-14T20:24:02Z jolly-indigo-vole: changed notes, summary; ticked acceptance criteria
- 2026-11-14T20:24:02Z jolly-indigo-vole doing → review
- 2026-11-14T20:27:35Z plucky-bronze-marten: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-14T20:27:35Z plucky-bronze-marten review → doing
- 2026-11-14T20:38:06Z rosy-silver-marten: changed notes, summary; ticked acceptance criteria
- 2026-11-14T20:38:06Z rosy-silver-marten doing → review
