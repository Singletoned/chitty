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

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
482 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 585 test suites (585 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 20:39:10 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
......................F.......................................................................Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp88qpzu01...
.......................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
......./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/CLAUDE.md
..Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/.worktrees/task-1...
..............................TASK-1: doing → review
..........chitty 0.1.31 is out: run uv tool upgrade chitty
...no next ticket for --mode work
........E...FFFFFFF...............landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_mcp_next_follows_workflow (tests.test_workflow_commands.TestWorkflowCommands.test_mcp_next_follows_workflow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 92, in test_mcp_next_follows_workflow
    self.assertNotIn("next", tool_names(self.root))
                             ~~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 28, in tool_names
    return {tool.name for tool in asyncio.run(create_server(start).list_tools())}
                                              ~~~~~~~~~~~~~^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/src/chitty/mcp.py", line 74, in create_server
    text = repository_guide(start_dir)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/src/chitty/store.py", line 1050, in repository_guide
    workflow = "runner" if root is None else load_repo_config(root).workflow
                                             ~~~~~~~~~~~~~~~~^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/src/chitty/config.py", line 230, in load_repo_config
    raise ChittyError(f"{source}: invalid TOML: {error}") from None
chitty.errors.ChittyError: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuk_s0yx9/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)

======================================================================
test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty (tests.test_next.TestNext.test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_next.py", line 1057, in test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty
    self.run_cli("init")
    ~~~~~~~~~~~~^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_cli.py", line 90, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0 : Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjba2nd66/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)


======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['run'], command='run')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty run needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['run', '--json'], command='run')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty run needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['run', '--help'], command='run')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 50, in test_tickets_commands_refuse
    self.assertEqual(result.exit_code, 1, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : Usage: cli run [OPTIONS]

  Run the next ticket, or the one named by --ticket; other arguments go to the
  agent.

Options:
  --ticket ID           Run the next ticket, or the one named by --ticket.
  --owner TEXT          Choose tickets owned by this agent.
  --agent NAME          Use the named command from [agent_commands].
  --errors              Repair error tickets only.
  --loop                Keep running; wait 60 seconds between attempts,
                        including when idle. Stop on errors.
  --mode [work|review]  Choose only tickets to work (doing, todo) or review.
                        Repeat to allow both.
  --help                Show this message and exit.


======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['next'], command='next')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty next needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['next', '--json'], command='next')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty next needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['next', '--help'], command='next')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 50, in test_tickets_commands_refuse
    self.assertEqual(result.exit_code, 1, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : Usage: cli next [OPTIONS]

  Print the next ticket to work or review.

Options:
  --owner TEXT          Choose tickets owned by this agent.
  --mode [work|review]  Choose only tickets to work (doing, todo) or review.
                        Repeat to allow both.
  --json                Print JSON.
  --help                Show this message and exit.


======================================================================
test_tickets_help_hides_run_and_next (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_help_hides_run_and_next)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 38, in test_tickets_help_hides_run_and_next
    self.assertNotIn("run", commands)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: 'run' unexpectedly found in {'fix', 'suggest', 'path', 'Markdown-native', 'show', 'next', 'mcp', 'pull', 'renumber', 'check', '--help', 'Tasks', 'init', 'list', 'archive', 'guide', 'Coding', 'move', 'run', 'inbox', '--version', 'TASK-13);', 'edit', 'whoami', 'note', 'add', 'import'}

----------------------------------------------------------------------
Ran 585 tests in 40.580s

FAILED (failures=8, errors=1)
make: *** [check] Error 9

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-333`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
482 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 585 test suites (585 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 20:39:10 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
......................F.......................................................................Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp88qpzu01...
.......................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
......./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/CLAUDE.md
..Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj712ieeu/repo/.worktrees/task-1...
..............................TASK-1: doing → review
..........chitty 0.1.31 is out: run uv tool upgrade chitty
...no next ticket for --mode work
........E...FFFFFFF...............landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_mcp_next_follows_workflow (tests.test_workflow_commands.TestWorkflowCommands.test_mcp_next_follows_workflow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 92, in test_mcp_next_follows_workflow
    self.assertNotIn("next", tool_names(self.root))
                             ~~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 28, in tool_names
    return {tool.name for tool in asyncio.run(create_server(start).list_tools())}
                                              ~~~~~~~~~~~~~^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/src/chitty/mcp.py", line 74, in create_server
    text = repository_guide(start_dir)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/src/chitty/store.py", line 1050, in repository_guide
    workflow = "runner" if root is None else load_repo_config(root).workflow
                                             ~~~~~~~~~~~~~~~~^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/src/chitty/config.py", line 230, in load_repo_config
    raise ChittyError(f"{source}: invalid TOML: {error}") from None
chitty.errors.ChittyError: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuk_s0yx9/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)

======================================================================
test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty (tests.test_next.TestNext.test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_next.py", line 1057, in test_run_stops_before_pi_when_refresh_fails_or_setup_is_dirty
    self.run_cli("init")
    ~~~~~~~~~~~~^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_cli.py", line 90, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0 : Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjba2nd66/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)


======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['run'], command='run')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty run needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['run', '--json'], command='run')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty run needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['run', '--help'], command='run')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 50, in test_tickets_commands_refuse
    self.assertEqual(result.exit_code, 1, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : Usage: cli run [OPTIONS]

  Run the next ticket, or the one named by --ticket; other arguments go to the
  agent.

Options:
  --ticket ID           Run the next ticket, or the one named by --ticket.
  --owner TEXT          Choose tickets owned by this agent.
  --agent NAME          Use the named command from [agent_commands].
  --errors              Repair error tickets only.
  --loop                Keep running; wait 60 seconds between attempts,
                        including when idle. Stop on errors.
  --mode [work|review]  Choose only tickets to work (doing, todo) or review.
                        Repeat to allow both.
  --help                Show this message and exit.


======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['next'], command='next')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty next needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['next', '--json'], command='next')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 51, in test_tickets_commands_refuse
    self.assertIn(
    ~~~~~~~~~~~~~^
        f'chitty {command} needs workflow = "runner" in the Chitty config',
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        result.stderr,
        ^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'chitty next needs workflow = "runner" in the Chitty config' not found in 'Error: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9q61j6hp/repo/chitty.toml: invalid TOML: Cannot overwrite a value (at line 5, column 20)\n'

======================================================================
test_tickets_commands_refuse (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_commands_refuse) (args=['next', '--help'], command='next')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 50, in test_tickets_commands_refuse
    self.assertEqual(result.exit_code, 1, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : Usage: cli next [OPTIONS]

  Print the next ticket to work or review.

Options:
  --owner TEXT          Choose tickets owned by this agent.
  --mode [work|review]  Choose only tickets to work (doing, todo) or review.
                        Repeat to allow both.
  --json                Print JSON.
  --help                Show this message and exit.


======================================================================
test_tickets_help_hides_run_and_next (tests.test_workflow_commands.TestWorkflowCommands.test_tickets_help_hides_run_and_next)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-333/tests/test_workflow_commands.py", line 38, in test_tickets_help_hides_run_and_next
    self.assertNotIn("run", commands)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: 'run' unexpectedly found in {'fix', 'suggest', 'path', 'Markdown-native', 'show', 'next', 'mcp', 'pull', 'renumber', 'check', '--help', 'Tasks', 'init', 'list', 'archive', 'guide', 'Coding', 'move', 'run', 'inbox', '--version', 'TASK-13);', 'edit', 'whoami', 'note', 'add', 'import'}

----------------------------------------------------------------------
Ran 585 tests in 40.580s

FAILED (failures=8, errors=1)
make: *** [check] Error 9

```
````

Landing failed after merging `main`: `TASK-335` (`e9d3db0`) pinned `workflow = "runner"` in `tests.support.CONFIG`, and this branch added a second `workflow` line in `tests/test_workflow_commands.py` and `tests/test_next.py`, so the fixture became invalid TOML (8 failures, 1 error, reproduced in the worktree). Fixed in the branch by the human session: `config_with` now replaces the pinned line, and the now-redundant `test_next.py` change is dropped. `make check` passes. Ready for an independent review.

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
- 2026-11-14T20:39:41Z daring-zinc-newt: changed notes
- 2026-11-14T20:39:41Z daring-zinc-newt review → error
- 2026-11-16T10:27:43Z intrepid-coral-raven: changed notes
- 2026-11-16T10:27:43Z intrepid-coral-raven error → review
