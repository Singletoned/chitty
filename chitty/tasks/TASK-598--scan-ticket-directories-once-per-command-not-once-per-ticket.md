---
title: Scan ticket directories once per command, not once per ticket, so `chitty list` is quick
status: cold-read
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: making `chitty list` quicker is a top priority. On this repository (415 active and 182 archived files in `chitty/tasks`, about a dozen ticket branches) `chitty list` takes about 22 s.

Profiled on 2026-11-22 (`cProfile` over `chitty.cli.main` with `list`): Git is not the cost (71 `subprocess.run` calls, about 1 s). The cost is re-listing ticket directories per ticket:

- `Repo._working_ticket_files(task_id)` (`src/chitty/store.py`, about line 470) walks every context directory, active and archive, through `_files` and `scan`, and keeps the files whose name parses to `task_id`. It is called once per ticket id looked up, across refs (2299 calls in the profile), so one `chitty list` makes 13,800 `scan` calls and 4.3 million `ids.parse_filename` calls (39 s of 49 s under the profiler).
- `Repo.discovered_contexts()` (about line 306) walks every ref's file list on each call; `context_of` calls it per dependency (251 calls, 6.9 s).
- `Repo._ref_ticket_files(ref, task_id)` walks the whole file list of `ref` per ticket (3.7 s).

Change, all in `Repo` in `src/chitty/store.py`; caches are per `Repo` object and cleared in `Repo._invalidate`, like the existing `_ticket_ids` and `_task_locations`:

- Build one working-tree index, `TaskId` to the list of paths, in a single pass over every context directory (active and archive), and use it in `_working_ticket_files` and `_collect_ticket_ids`. Keep today's order of paths and today's errors: an invalid entry anywhere still raises the same `ChittyError` from `_files`, whichever ticket was asked for.
- Index each ref's ticket files by `TaskId` once, and use it in `_ref_ticket_files`.
- Cache the result of `discovered_contexts()`.

Behaviour is unchanged; only the number of directory scans changes. Clear the new caches in `Repo._invalidate`.

Tests, in `tests/test_list_performance.py` next to the existing constant-Git-calls tests, which they mirror.

Scan-count fixture, built by a helper taking the active ticket count `n`: a Git repository (`git init -b main`, an identity, as `_list_git_calls` does) whose `chitty.toml` is `_list_git_calls`'s plus a second context `[contexts.backlog]` with `prefix = "BACK"`; `n` active tickets `TASK-1` to `TASK-n` in `chitty/tasks/`, one archived `TASK-1000` in `chitty/tasks/archive/`, one `BACK-1` in `chitty/backlog/`; all committed on `main`. Then `git worktree add -b task-2 <tmp>/wt-task-2 main`, change `TASK-2`'s title there to `Branch copy` and commit it on `task-2`. So 4 context directories exist (`tasks`, `tasks/archive`, `backlog`, `backlog/archive`, the last empty).

Run each count in a subprocess with `cwd` at the repository, as the existing tests do: a short `python -c` script that replaces `chitty.store.scan` with a counting wrapper of the original, then either calls `chitty.cli.cli(["list"], standalone_mode=False)`, or opens `Repo.open(Path.cwd())` and calls `repo.lookup(task_id)` for every id in `repo.ticket_ids()`; it prints the count (and, for the lookup script, `TASK-2`'s title). For `n` = 2 and 20, assert the counts are equal, and between 4 and 8 inclusive (one or two scans of each of the 4 directories; `scan` is called per directory, active or archive), and that `TASK-2`'s title is `Branch copy`.

Error and order cases, in-process through `Repo.open(root)`, in a directory that is not a Git repository (do not `git init`), so `_working_ticket_files` is the path used; config as above. Run each against `main` before the change and record the messages in a note; assert the exact messages:

- `chitty/tasks/not-a-ticket.md` present: `repo.lookup` of an unrelated ticket raises `ChittyError` whose message starts with the file's absolute path followed by `: `.
- The same with the bad file in `chitty/backlog/archive/` instead.
- `TASK-3` present in both `chitty/tasks/` and `chitty/tasks/archive/`: `repo.lookup(TASK-3)` raises `TASK-3 is used by more than one file: ` followed by the two absolute paths, active first, joined by `, `.

Out of scope: other commands' speed, and Git calls (already constant in the ticket count).

## Acceptance Criteria

- [ ] The scan-count tests (`chitty list` and `lookup` of every ticket: equal for 2 and 20 tickets, between 4 and 8 scans, `TASK-2` read from its branch) and the three error and order tests pass; the scan-count tests fail before the change. Record both runs in a note
- [ ] Before and after the change, in the main checkout at the same `main` commit with ticket branches unchanged between runs: `chitty list`, `chitty list -s backlog` and `chitty list --all` print byte-identical output, where "before" is the main checkout's `.venv/bin/chitty` and "after" is the ticket worktree's `.venv/bin/chitty` (run `make install` in the worktree first) run with `cwd` at the main checkout. Record the `diff` result and three `time` runs of `chitty list` for each in a note
- [ ] `make check` passes

## History

- 2026-11-22T21:26:10Z plucky-umber-wren → cold-read
- 2026-11-22T21:26:19Z plucky-umber-wren: changed acceptance criteria
- 2026-11-22T21:29:16Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:31:17Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:31:26Z plucky-umber-wren: changed description, acceptance criteria
