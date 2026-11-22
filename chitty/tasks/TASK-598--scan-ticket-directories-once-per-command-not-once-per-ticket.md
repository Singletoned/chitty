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

Behaviour is unchanged; only the number of directory scans changes. Clear the new caches in `Repo._invalidate`.

Tests, in `tests/test_list_performance.py` next to the existing constant-Git-calls tests, which they mirror: build a repository the way `_list_git_calls` does (one `tasks` context, one archived ticket in `chitty/tasks/archive/`, and a ticket branch `task-2` in a linked worktree whose copy of `TASK-2` differs from `main`'s), with 2 and then 20 active tickets. Run the listing in a subprocess with `cwd` at that repository, as the existing tests do, so nothing in-process needs `os.chdir`: a short `python -c` script that wraps `chitty.store.scan` with a counting function (`chitty.store.scan = counted(chitty.store.scan)`), then calls `chitty.cli.cli(["list"], standalone_mode=False)` and prints the count. A second script does the same around `repo.lookup(task_id)` for every id in `repo.ticket_ids()`. Assert, for each script, that the counts for 2 and 20 tickets are equal and are at most 2 per context directory (active and archive; `tasks` and any other directory under `chitty/`), so "once per command" is shown, not only "constant". The lookup script also prints `TASK-2`'s title and source ref; assert they are the branch copy's.

Error and order cases, same file, run once each through `Repo.open(root)` in-process (no counting): with a file `chitty/tasks/not-a-ticket.md` present, `repo.lookup` of an unrelated ticket raises `ChittyError` whose message starts with that file's path, as on `main`; with `TASK-3` both in `chitty/tasks/` and `chitty/tasks/archive/`, `repo.lookup(TASK-3)` raises `TASK-3 is used by more than one file: ` followed by the two paths in the same order `main` gives (active first, as `_working_ticket_files` lists them today). Run both against `main` first and record the messages in a note; assert those exact messages.

Out of scope: other commands' speed, and Git calls (already constant in the ticket count).

## Acceptance Criteria

- [ ] The scan-count tests (`chitty list` and `lookup` of every ticket: equal for 2 and 20 tickets, at most 2 scans per context directory, `TASK-2` read from its branch) and the error and order tests pass; the scan-count tests fail before the change. Record both runs in a note
- [ ] Before and after the change, in the main checkout at the same `main` commit with ticket branches unchanged between runs: `chitty list`, `chitty list -s backlog` and `chitty list --all` print byte-identical output, where "before" is the main checkout's `.venv/bin/chitty` and "after" is the ticket worktree's `.venv/bin/chitty` run with `cwd` at the main checkout. Record the `diff` result and three `time` runs of `chitty list` for each in a note
- [ ] `make check` passes

## History

- 2026-11-22T21:26:10Z plucky-umber-wren → cold-read
- 2026-11-22T21:26:19Z plucky-umber-wren: changed acceptance criteria
- 2026-11-22T21:29:16Z plucky-umber-wren: changed description, acceptance criteria
