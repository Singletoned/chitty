---
title: Scan ticket directories once per command, not once per ticket, so `chitty list` is quick
status: cold-read
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: making `chitty list` quicker is a top priority. On this repository (415 active and 182 archived files in `chitty/tasks`, about a dozen ticket branches) `chitty list` takes about 22 s.

Profiled on 2026-11-22 (`cProfile` over `chitty.cli.main` with `list`): Git is not the cost (71 `subprocess.run` calls, about 1 s). The cost is re-listing ticket directories per ticket:

- `Repo._working_ticket_files(task_id)` (`src/chitty/store.py`, about line 470) walks every context directory, active and archive, through `_files` and `scan`, and keeps the files whose name parses to `task_id`. It is called once per ticket (2299 calls), so one `chitty list` makes 13,800 `scan` calls and 4.3 million `ids.parse_filename` calls (39 s of 49 s under the profiler).
- `Repo.discovered_contexts()` (about line 306) walks every ref's file list on each call; `context_of` calls it per dependency (251 calls, 6.9 s).
- `Repo._ref_ticket_files(ref, task_id)` walks the whole file list of `ref` per ticket (3.7 s).

Change, all in `Repo` in `src/chitty/store.py`; caches are per `Repo` object and cleared in `Repo._invalidate`, like the existing `_ticket_ids` and `_task_locations`:

- Build one working-tree index, `TaskId` to the list of paths, in a single pass over every context directory (active and archive), and use it in `_working_ticket_files` and `_collect_ticket_ids`. Keep today's order of paths and today's errors: an invalid entry anywhere still raises the same `ChittyError` from `_files`, whichever ticket was asked for.
- Index each ref's ticket files by `TaskId` once, and use it in `_ref_ticket_files`.
- Cache the result of `discovered_contexts()`.

Behaviour is unchanged; only the number of directory scans changes.

Tests, in `tests/test_list_performance.py` next to the existing constant-Git-calls tests: the same shape, counting calls to `chitty.store.scan` instead of Git calls. Build a repository like `_list_git_calls` does with 2 and then 20 tickets, run `Repo.open(root)` and the same listing the `list` command does (`chitty.cli.main` with `["list"]` through `click.testing.CliRunner`, run in the repository), with `unittest.mock.patch("chitty.store.scan", wraps=chitty.store.scan)` to count calls; assert the two counts are equal. Do the same for `repo.lookup(task_id)` over every ticket, as `_lookup_git_calls` does. This is a spy on a pure function, not filesystem mocking.

Out of scope: other commands' speed, and Git calls (already constant in the ticket count).

## Acceptance Criteria

- [ ] The two new tests in `tests/test_list_performance.py` (scan calls for `chitty list`, and for `lookup` of every ticket, equal for 2 and 20 tickets) pass, and fail before the change; record both runs in a note
- [ ] Run in the main checkout before and after the change, `chitty list`, `chitty list -s backlog` and `chitty list -a` (with `.venv/bin/chitty` of each version, the same `main` commit, ticket branches unchanged between runs) print byte-identical output; record the `diff` result and the `time` of `chitty list` before and after in a note
- [ ] `make check` passes

## History

- 2026-11-22T21:26:10Z plucky-umber-wren → cold-read
