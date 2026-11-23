---
title: Scan ticket directories once per command, not once per ticket, so `chitty list` is quick
status: doing
priority: high
depends_on:
  - TASK-639
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: making `chitty list` quicker is a top priority. On this repository (415 active and 182 archived files in `chitty/tasks`, about a dozen ticket branches) `chitty list` takes about 19 s (measured 2026-11-23, after TASK-639 cached `discovered_contexts`).

Profiled on 2026-11-22 and again on 2026-11-23 after TASK-639 (`cProfile` over `chitty.cli.main` with `list`): Git is not the cost (71 `subprocess.run` calls, about 1 s). The cost is re-listing ticket directories per ticket:

- `Repo._working_ticket_files(task_id)` (`src/chitty/store.py`, about line 470) walks every context directory, active and archive, through `_files` and `scan`, and keeps the files whose name parses to `task_id`. It is called once per ticket id looked up, across refs so one `chitty list` makes 14,802 `scan` calls (2026-11-23 count); under the profiler `_working_ticket_files` took 156 s of 166 s and `ids.parse_filename` 42 s.
- `Repo._ref_ticket_files(ref, task_id)` walks the whole file list of `ref` per ticket (3.7 s).

Change, all in `Repo` in `src/chitty/store.py`; caches are per `Repo` object and cleared in `Repo._invalidate`, like the existing `_ticket_ids` and `_task_locations`:

- Build one working-tree index, `TaskId` to the list of paths, in a single pass over every context directory (active and archive), and use it in `_working_ticket_files` and `_collect_ticket_ids`. Keep today's order of paths and today's errors: an invalid entry anywhere still raises the same `ChittyError` from `_files`, whichever ticket was asked for.
- Index each ref's ticket files by `TaskId` once, and use it in `_ref_ticket_files`. Reuse or replace the existing `_ticket_ref_files` cache; do not add a second cache for the same data.
- The working-tree index walks every child directory of `chitty/`, as `_working_ticket_files` and `_collect_ticket_ids` do today, not only configured contexts; that is unchanged.
- The `discovered_contexts()` cache is TASK-639, which lands first.

Behaviour is unchanged; only the number of directory scans changes. One accepted difference: a file added by hand while one `Repo` object is alive is not seen until `_invalidate` runs. A `Repo` lives for one command or MCP call, and Chitty's own writes already call `_invalidate`. On refs, keep today's asymmetry: a ref file whose name does not parse is skipped (`_ref_ticket_files`), while a bad working-tree entry raises. Clear the new caches in `Repo._invalidate`.

Tests, in `tests/test_list_performance.py` next to the existing constant-Git-calls tests, which they mirror.

Scan-count fixture, built by a helper taking the active ticket count `n`: a Git repository (`git init -b main`, an identity, as `_list_git_calls` does) whose `chitty.toml` is `_list_git_calls`'s plus a second context `[contexts.backlog]` with `prefix = "BACK"`; `n` active tickets `TASK-1` to `TASK-n` in `chitty/tasks/`, one archived `TASK-1000` in `chitty/tasks/archive/`, one `BACK-1` in `chitty/backlog/`; all committed on `main`. Then `git worktree add -b task-2 <tmp>/wt-task-2 main`, change `TASK-2`'s title there to `Branch copy` and commit it on `task-2`. So 4 context directories exist (`tasks`, `tasks/archive`, `backlog`, `backlog/archive`). `backlog/archive` does not exist on disk, since Git keeps no empty directory; `scan` is still called for it and returns `[]`, so it counts as one scan. Use the same fixture helper and test file for the run against the committed state before the change and the run after it.

Run each count in a subprocess with `cwd` at the repository, as the existing tests do: a short `python -c` script that replaces `chitty.store.scan` with a counting wrapper of the original, then either calls `chitty.cli.cli(["list"], standalone_mode=False)`, or opens `Repo.open(Path.cwd())` and calls `repo.lookup(task_id)` for every id in `repo.ticket_ids()`; it prints the count (and, for the lookup script, `TASK-2`'s title, `repo.lookup(TASK-2).task.frontmatter.title`). For `n` = 2 and 20, assert the counts (for the whole script) are equal, and between 4 and 8 inclusive (one or two scans of each of the 4 directories; `scan` is called per directory, active or archive), and that `TASK-2`'s title is `Branch copy`.

Error and order cases, in-process through `Repo.open(root)`, in a directory that is not a Git repository (do not `git init`), so `_working_ticket_files` is the path used; config as above. Run each against `main` before the change and record the messages in a note; assert the exact messages:

- `chitty/tasks/not-a-ticket.md` present: `repo.lookup` of an unrelated ticket raises `ChittyError` whose message starts with `str(root / "chitty/tasks/not-a-ticket.md")` followed by `: `, with `root` exactly as passed to `Repo.open` (not resolved).
- The same with the bad file in `chitty/backlog/archive/` instead.
- `TASK-3` present in both `chitty/tasks/` and `chitty/tasks/archive/`: `repo.lookup(TASK-3)` raises `TASK-3 is used by more than one file: ` followed by the two absolute paths, active first, joined by `, `.
- A ref case, in a Git repository with the scan-count fixture plus a committed file `chitty/tasks/not-a-ticket.md` on `task-2` only: `lookup` of `TASK-1` returns the ticket, with its committed title, and `lookup` of `TASK-2` returns title `Branch copy` (this one reads `task-2`'s files, so it reaches the unparseable name and must skip it).

Property, same file, with Hypothesis: draw a set of ticket file names of the form `<ID>--<slug>.md` (ids from `TASK-1` to `TASK-5` and `BACK-1` to `BACK-3`, slugs drawn with `st.text(string.ascii_lowercase, min_size=1)`), each placed in one of the four directories, duplicates of one id allowed; write them in a new non-Git directory per example (`tempfile.mkdtemp(dir=self.tmp)`) with the config above, each a valid ticket (frontmatter `title`, `status: todo`, `priority: medium`, `created`, and a `## Description` section) whose title is its file name without `.md`, so the returned ticket's title identifies the path. Duplicate draws with the same path count once; a `BACK-` id may be placed in `tasks/` (`_files` accepts any prefix), and is then returned with `context == "tasks"`, as today. For every id from `TASK-1` to `TASK-5` and `BACK-1` to `BACK-3`, `repo.lookup(id)` returns `None` when no file was drawn for it, or else returns the ticket from the one path, or raises the "used by more than one file" message listing that id's paths in the order `_working_ticket_files` gives today: context directories in sorted name order, each active then archive (`backlog`, `backlog/archive`, `tasks`, `tasks/archive`), and within a directory sorted by name. Use `examples(100)` from `tests/__init__.py` for `max_examples`.

Out of scope: other commands' speed, and Git calls (already constant in the ticket count).

The branch `task-598` was rebased onto `main` on 2026-11-23, so TASK-639's cache is in the baseline. Rebase again before starting if `main` has moved; criterion 2's "before" is the rebased branch's merge-base with `main`.

Invalidation example, same file, in a non-Git directory with the config above (`archive = "move"`, the default) and `TASK-1` active with status `done`: on one `Repo` object, `lookup(TASK-1)` (fills the caches), then `repo.archive(TASK-1)`, then `lookup(TASK-1)` returns it with `archived` true; then `change = repo.add(repo.context("tasks"), "New", None, [], {}, date(2026, 11, 23))` (the signature at `Repo.add` in `src/chitty/store.py`), then `lookup(change.task.id)` returns it. Without clearing the new caches in `_invalidate`, the second lookups return stale results. The property covers ids and paths only; the error examples cover invalid entries.

## Acceptance Criteria

- [ ] The scan-count tests (`chitty list` and `lookup` of every ticket: equal for 2 and 20 tickets, between 4 and 8 scans, `TASK-2` read from its branch), the three error and order tests, the ref case, the invalidation example and the property pass; the scan-count tests fail before the change. Record both runs in a note
- [ ] Before and after the change, run with `cwd` at the ticket worktree and with no ticket commits made between runs: `chitty list`, `chitty list -s backlog` and `chitty list --all` each print non-empty, byte-identical output. "After" is the worktree's own `.venv/bin/chitty`. For "before", run `mkdir -p tmp/before && git archive "$(git merge-base main HEAD)" src | tar -x -C tmp/before`, then use `PYTHONPATH=tmp/before/src .venv/bin/python -c "from chitty.cli import main; main()"` with the same arguments. Record the `diff` result and three `time` runs of `chitty list` for each in a note
- [ ] `make check` passes

## Plan

Build regression tests for scan counts, ordering, errors, refs and invalidation; record baseline, index working and ref files per Repo, then compare output and run checks.

## Notes

Acceptance criterion 2 requires running both executables with cwd in the main checkout, reading its ticket files and refs and writing comparison evidence. The session instruction restricts all reads and changes to this ticket worktree, so that verification is not authorized. Please decide whether to authorize the main-checkout benchmark or revise the criterion to use an isolated fixture in this worktree. Until then the required byte-identical outputs and timing runs cannot be checked.

Inspected the remaining requirements: the working-tree and ref scans, discovered-context cache, existing performance tests, and invalidation are present in the stated locations. The requested regression, error/order, ref and property tests and make check can be performed in the worktree, but implementation has not begun because criterion 2 is blocked. No other actionable ticket defects were found in this inspection.

Planner, 2026-11-23: the blocker is resolved by rewriting criterion 2 so that it runs entirely inside the ticket worktree. That worktree shares the repository's refs and holds the full set of ticket files, and the "before" code is taken from the merge base with `git archive`. Nothing reads the main checkout.

Planner, 2026-11-23, after a cold read: on 2026-11-23 a counting wrapper gave 36 `scan` calls for `chitty list` on this repository (15.6 s), not the 13,800 the Description reports, while `discovered_contexts` took 67 s of 90 s under cProfile. That cache is split out as TASK-639, which this ticket now depends on. Before planning resumes, profile again after TASK-639 lands, and narrow or drop this ticket if scans are no longer a real cost. Also fixed: the context order claim (`backlog` before `tasks`), the property's `None` outcome, path de-duplication and cross-prefix placement, the `mkdir` for `tmp/before`, and the title assertion in the ref case.

Planner, 2026-11-23, after TASK-639 landed: `chitty list` takes 19.3 s real on this repository. A counting wrapper gave 14,802 `scan` calls (the earlier count of 36 was wrong), and under cProfile `Repo._working_ticket_files` took 156 s of 166 s, `ids.parse_filename` 42 s. Scans are still the cost, so the ticket stands as written.

## History

- 2026-11-22T21:26:10Z plucky-umber-wren → cold-read
- 2026-11-22T21:26:19Z plucky-umber-wren: changed acceptance criteria
- 2026-11-22T21:29:16Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:31:17Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:31:26Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:33:00Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T21:33:00Z plucky-umber-wren cold-read → todo
- 2026-11-22T21:36:27Z witty-khaki-falcon todo → doing
- 2026-11-22T21:38:29Z witty-khaki-falcon: changed owner, notes
- 2026-11-22T21:38:29Z witty-khaki-falcon doing → planning
- 2026-11-23T12:03:08Z witty-russet-gannet: changed acceptance criteria, notes
- 2026-11-23T12:03:08Z witty-russet-gannet planning → cold-read
- 2026-11-23T12:08:50Z witty-russet-gannet: changed dependencies, description, acceptance criteria, notes
- 2026-11-23T12:08:50Z witty-russet-gannet cold-read → planning
- 2026-11-23T13:46:00Z youthful-quartz-zander: changed notes
- 2026-11-23T14:30:11Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:31:14Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:31:17Z youthful-quartz-zander: changed description
- 2026-11-23T14:31:21Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:34:15Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:34:20Z youthful-quartz-zander: changed description
- 2026-11-23T14:34:25Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:35:57Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:36:00Z youthful-quartz-zander: changed description
- 2026-11-23T14:36:03Z youthful-quartz-zander: changed acceptance criteria
- 2026-11-23T14:36:07Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:36:24Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:36:27Z youthful-quartz-zander: changed description
- 2026-11-23T14:36:30Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:38:08Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:38:11Z youthful-quartz-zander: changed description
- 2026-11-23T14:38:17Z youthful-quartz-zander planning → cold-read
- 2026-11-23T14:38:19Z youthful-quartz-zander cold-read → planning
- 2026-11-23T14:38:22Z youthful-quartz-zander planning → todo
- 2026-11-23T14:39:51Z jolly-white-urchin todo → doing
- 2026-11-23T14:44:11Z jolly-white-urchin: wrote the plan
