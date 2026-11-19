---
title: Parse only the dependency's file when checking a dependency on `main`
status: doing
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

- [ ] The test returns `True` and counts exactly one `parse` call; against the old `_dependency_is_done` it counts at least eleven (recorded in the notes)
- [ ] A test with a malformed body in a ticket other than the dependency on `main` still reports the dependency done; against the old code it raises `ChittyError` (recorded in the notes)
- [ ] `chitty list` in this repository is timed before and after in the notes; `make check` passes

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

## History

- 2026-11-19T14:29:04Z quick-ginger-lapwing → doing
- 2026-11-19T14:31:01Z plucky-umber-wren: changed notes
- 2026-11-19T14:31:14Z plucky-umber-wren: wrote the plan
