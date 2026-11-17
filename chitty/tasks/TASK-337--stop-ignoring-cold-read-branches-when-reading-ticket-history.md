---
title: Stop ignoring `cold-read/` branches when reading ticket history
status: doing
depends_on:
  - TASK-336
created: 2026-11-16
---

## Description

Cold reads are read-only now (`TASK-336`), so nothing creates `cold-read/` branches. `_is_cold_read_ref` in `src/chitty/git.py` and its use in `historical_files` (the `not _is_cold_read_ref(ref)` filter) only exist to keep such branches out of ticket history. Remove the function and the filter, and the two tests `test_local_cold_read_branch_is_not_a_source` and `test_remote_cold_read_branch_is_not_a_source` in `tests/test_cli.py`, and their helper `make_newer_copy_on`, which nothing else uses. A clone that still has old `cold-read/` branches reads them as ordinary history afterwards; that is accepted, because the newest commit of a ticket wins and readers never wrote ticket files. Refs under `refs/cold-read/` are not branches and were never read; leave them alone.

No property test and no test that fails first: this removes code; existing history tests cover the remaining behaviour.

## Acceptance Criteria

- [ ] `git grep -n -e _is_cold_read_ref -e cold_read_branch -e make_newer_copy_on -- src tests` prints nothing. `make check` passes.

## Plan

Remove the cold-read ref predicate/filter and the two obsolete cold-read history tests plus their helper. Run the required grep and full make check, then record verification and commit implementation changes.

## History

- 2026-11-16T09:50:18Z intrepid-coral-raven → backlog
- 2026-11-16T09:50:27Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:25Z intrepid-coral-raven backlog → planning
- 2026-11-16T12:51:10Z open-russet-eel: changed description
- 2026-11-16T16:57:06Z open-russet-eel: changed title, description, acceptance criteria
- 2026-11-16T16:57:29Z open-russet-eel: changed owner
- 2026-11-16T16:57:29Z open-russet-eel planning → cold-read
- 2026-11-16T16:58:17Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:58:17Z open-russet-eel cold-read → planning
- 2026-11-16T16:58:19Z open-russet-eel: changed owner
- 2026-11-16T16:58:19Z open-russet-eel planning → todo
- 2026-11-17T17:29:59Z rosy-zinc-yellowhammer todo → doing
- 2026-11-17T17:30:16Z rosy-zinc-yellowhammer: wrote the plan
