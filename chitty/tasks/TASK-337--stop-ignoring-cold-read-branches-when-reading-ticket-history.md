---
title: Stop ignoring `cold-read/` branches when reading ticket history
status: cold-read
owner: open-russet-eel
depends_on:
  - TASK-336
created: 2026-11-16
---

## Description

Cold reads are read-only now (`TASK-336`), so nothing creates `cold-read/` branches. `_is_cold_read_ref` in `src/chitty/git.py` and its use in `historical_files` (the `not _is_cold_read_ref(ref)` filter) only exist to keep such branches out of ticket history. Remove the function and the filter, and the two tests `test_local_cold_read_branch_is_not_a_source` and `test_remote_cold_read_branch_is_not_a_source` in `tests/test_cli.py`. Refs under `refs/cold-read/` are not branches and were never read; leave them alone.

No property test and no test that fails first: this removes code; existing history tests cover the remaining behaviour.

## Acceptance Criteria

- [ ] `git grep -n -e _is_cold_read_ref -e cold_read_branch -- src tests` prints nothing. `make check` passes.

## History

- 2026-11-16T09:50:18Z intrepid-coral-raven → backlog
- 2026-11-16T09:50:27Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:25Z intrepid-coral-raven backlog → planning
- 2026-11-16T12:51:10Z open-russet-eel: changed description
- 2026-11-16T16:57:06Z open-russet-eel: changed title, description, acceptance criteria
- 2026-11-16T16:57:29Z open-russet-eel: changed owner
- 2026-11-16T16:57:29Z open-russet-eel planning → cold-read
