---
title: Parse only the dependency's file when checking a dependency on `main`
status: review
priority: high
created: 2026-11-19
---

## Description

`chitty list` takes about 4 s in this repository. Profiling showed 8.7 s of 10.3 s in `_dependency_is_done` (`src/chitty/store.py`): for every dependency of every `todo` ticket it fully parses (`parse`, YAML and History) every ticket file on `main`, active and archived, and only then compares IDs. 34 dependency references gave 15,259 parses. `main`'s file list is already cached per `Repo` (`_main_files_for`), so only the parsing is wasted.

Decisions:

- In `_dependency_is_done`, run `ids.parse_filename` on every path first, as today, and call `parse` only on files whose ID equals `dependency_id`.
- A malformed file name still raises `ChittyError` naming `refs/heads/<main>:<path>`. A malformed body in a file that is not the dependency no longer does: it has nothing to do with this dependency. A malformed body in the dependency's own file still raises.

Test: in `tests/test_next.py`, next to `test_todo_dependency_must_be_done_on_main` and set up the same way (a Git repo on `main`, `autocommit = false`), add ten `done` tickets and a `todo` ticket depending on one of them, commit, then call `chitty.store._dependency_is_done` once with `chitty.store.parse` wrapped (by `unittest.mock.patch` with `wraps=`) to count calls. No property: this is a call count on fixed files.

## Acceptance Criteria

- [x] The test returns `True` and counts exactly one `parse` call; against the old `_dependency_is_done` it counts one per ticket file on `main` (recorded in the notes)
- [x] A test with a malformed body in a ticket other than the dependency on `main` still reports the dependency done; against the old code it raises `ChittyError` (recorded in the notes)
- [x] `chitty list` in this repository is timed before and after in the notes; `make check` passes

## Plan

Filter cached main-branch paths by parsed filename ID before parsing ticket contents. Add fixed-file regression tests for exact parse count and unrelated malformed body, verify both regressions fail on the old implementation, time chitty list before/after, then run make check and commit implementation.

## Notes

Check failed before this session: check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
I001 [*] Import block is un-sorted or un-formatted
  --> tests/test_next.py:1:1
   |
 1 | / import asyncio
 2 | | import io
 3 | | import json
 4 | | import os
 5 | | import stat
 6 | | import subprocess
 7 | | import sys
 8 | | from contextlib import redirect_stderr
 9 | | from pathlib import Path
10 | | from unittest.mock import patch
11 | | from uuid import UUID
12 | |
13 | | from mcp.server.mcpserver.exceptions import ToolError
14 | | from mcp_types import CallToolResult
15 | |
16 | | from chitty.config import CHITTY_VERSION
17 | | from chitty.errors import ChittyError
18 | | from chitty.inbox import suggest
19 | | from chitty.mcp import create_server
20 | | from chitty.run import _record_usage, run_loop
21 | | from chitty import store
22 | | from chitty.ids import TaskId
23 | | from chitty.store import Repo, guide, next_action, ticket_action
24 | | from tests.test_cli import CliTestCase
   | |______________________________________^
help: Organize imports
   |
15 |
16 + from chitty import store
17 | from chitty.config import CHITTY_VERSION
18 | from chitty.errors import ChittyError
19 + from chitty.ids import TaskId
20 | from chitty.inbox import suggest
21 | from chitty.mcp import create_server
22 | from chitty.run import _record_usage, run_loop
   - from chitty import store
   - from chitty.ids import TaskId
23 | from chitty.store import Repo, guide, next_action, ticket_action
   |

Found 1 error.
[*] 1 fixable with `--fix`.
make: *** [check] Error 1

```

Implemented by the planner, as the owner asked; reviewed by the normal reviewer.

Evidence, `.venv/bin/python -m unittest` on the two new tests in `tests/test_next.py`:
- Old code: `test_dependency_check_parses_only_the_dependency` fails with `AssertionError: 10 != 1` (ten files on `main`); `test_malformed_other_ticket_on_main_does_not_break_a_dependency` raises `ChittyError: refs/heads/main:chitty/tasks/TASK-2--done-1.md: frontmatter is not valid YAML`.
- New code: both pass.
- `chitty list` in the main checkout, two runs each: `real 4.23` and `4.25` with the Chitty of `main`; `real 1.29` and `1.29` with the Chitty of this branch.
- `make check`: `Ran 744 tests`, `OK`. One earlier run of `tests.test_next` failed only in `test_run_cases` (`TASK-1: blocked → error`, expected exit 3), the known flaky test from the inbox; it passed on rerun and in `make check`.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 744 test suites (744 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 14:34:19 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
...........................................................................................F................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/CLAUDE.md
....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/.worktrees/task-1...
.....TASK-1: doing → review
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/CLAUDE.md
no next ticket for --mode work
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/CLAUDE.md
................................................chitty 0.1.31 is out: run uv tool upgrade chitty
...............................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_run_cases (tests.test_next.TestNext.test_run_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-425/tests/test_next.py", line 1873, in test_run_cases
    no_next = self.run_cli("run", exit_code=3)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-425/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : TASK-1: blocked → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpm8hra5ro/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 744 tests in 41.623s

FAILED (failures=1)
make: *** [check] Error 1

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-425`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 744 test suites (744 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 14:34:19 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
...........................................................................................F................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/CLAUDE.md
....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa5i6diiw/repo/.worktrees/task-1...
.....TASK-1: doing → review
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnjepeet1/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp736eh_ej/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxaegwbpo/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy4qd0ari/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7v3xygo8/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps7a5uw7i/repo/CLAUDE.md
no next ticket for --mode work
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvwucy2iz/repo/CLAUDE.md
................................................chitty 0.1.31 is out: run uv tool upgrade chitty
...............................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_run_cases (tests.test_next.TestNext.test_run_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-425/tests/test_next.py", line 1873, in test_run_cases
    no_next = self.run_cli("run", exit_code=3)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-425/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : TASK-1: blocked → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpm8hra5ro/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 744 tests in 41.623s

FAILED (failures=1)
make: *** [check] Error 1

```
````

Reset 2026-11-19: the runner error came from the flaky `tests.test_next.TestNext.test_run_cases`, fixed on `main` in `fe1ef0cd`; back to `review`.

## Summary

Dependency checks on `main` now parse only the file of the dependency. `chitty list` here went from 4.2 s to 1.3 s. Verified by two new tests that fail on the old code and by `make check` (744 tests). No follow-up.

## History

- 2026-11-19T14:29:04Z quick-ginger-lapwing → doing
- 2026-11-19T14:31:01Z plucky-umber-wren: changed notes
- 2026-11-19T14:31:14Z plucky-umber-wren: wrote the plan
- 2026-11-19T14:32:56Z quick-ginger-lapwing: changed acceptance criteria
- 2026-11-19T14:33:08Z quick-ginger-lapwing: changed notes, summary; ticked acceptance criteria
- 2026-11-19T14:33:08Z quick-ginger-lapwing doing → review
- 2026-11-19T14:34:55Z upbeat-umber-eel: changed notes
- 2026-11-19T14:34:55Z upbeat-umber-eel review → error
- 2026-11-19T16:01:56Z quick-ginger-lapwing: changed notes
- 2026-11-19T16:01:56Z quick-ginger-lapwing error → review
