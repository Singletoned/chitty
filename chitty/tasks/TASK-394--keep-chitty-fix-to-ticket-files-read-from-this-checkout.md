---
title: Keep `chitty fix` to ticket files read from this checkout
status: cold-read
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-18
---

## Description

After `TASK-378`, a ticket in flight is read from its branch, but `chitty fix` (`fix` in `src/chitty/check.py`) still scans and rewrites this checkout's ticket files. In the main checkout it can rewrite `main`'s stale copy of an in-flight ticket, a write on `main` for a ticket with a branch, which the new model forbids (`docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`) and which `TASK-377` then reports as changed on both sides.

Starts after `TASK-378` lands.

Decisions:

- New `Repo.source_of(task_id) -> str | None` (in `src/chitty/store.py`, beside `TASK-378`'s map): the `ticket_source` result for that ID, as a short ref name (`refs/heads/task-5` gives `task-5`, `refs/remotes/origin/task-7` gives `origin/task-7`, as `SourceCopy.ref` does), or `None` for the working tree. It parses nothing: it uses `_choose_source` (`provisional` from the ID and file names, `TASK-504`), so a malformed file never stops it. Errors from `ticket_source` (diverged branches, a ticket changed on both sides) propagate.
- `fix` (which scans files with `scan`, not `Repo`) asks `source_of` for each scanned file's ID (from its filename), only for files inside the `paths` filter and after `scan` accepts the name, before parsing its content. It repairs the file only when `source_of` is `None` and the file is the only scanned working-tree file with that ID (count, by filename, every scanned working-tree ticket name in every context's active and archive directories, regardless of the `paths` filter and of whether the content parses; do not call `Repo.find`, which raises on duplicates). Decided 2026-11-21: when two or more working-tree files share an ID, `fix` cannot tell which is authoritative, so it repairs none of them and adds `Problem(path, "skipped: <ID> is used by more than one file", "warning")` for each one within the `paths` filter; `check` keeps reporting the duplicate as an error. Files that fail to scan or parse are left to the existing repair loop and to `check`, exactly as today (`tests/test_check.py` `test_fix_reports_unresolved_problems_without_writing` must still pass). Any other file (read from another ref, or absent from the map, for example `main`'s copy of a ticket whose slug changed on its branch) is not repaired and is reported as a warning `Problem(path, "skipped: read from <ref>", "warning")` in `fix`'s problems list (the second element it returns), only for files within the `paths` filter; `errors()` ignores warnings and the CLI already prints problems. In a ticket worktree this also skips tickets read from `main`: intended.
- Errors from `source_of` propagate; never catch them in the existing `except ChittyError: continue`. A diverged ticket therefore stops `fix`, loudly, as decided. Relies on `TASK-378`'s contract that a working-tree read has `branch is None`, including on the ticket's own branch.
- `chitty check` keeps checking every file in this checkout, as a file-format check.

Tests: real-Git tests in a new `tests/test_fix_sources.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`. The fixable defect is a lower-case reference, `depends_on: [task-3]`, which `fix` rewrites to `TASK-3`; `main`'s copy of an in-flight ticket is committed directly with Git. No property: a fixed set of file sources, each in the criteria.

## Acceptance Criteria

- [ ] In the main checkout, with `main`'s copy of `TASK-5` holding `depends_on: [task-3]` committed before `task-5` is created, and `task-5` then getting its own commit changing only another file (so `main`'s copy is unchanged since the split and the branch is ahead), `chitty fix` leaves `main`'s file byte-identical, lists a `skipped: read from task-5` warning and leaves `HEAD` unchanged (fails before the change); the same defect in a ticket with no branch is rewritten to `TASK-3` (passes before and after); with `main`'s copy named `TASK-5--old.md` and `task-5` renaming it to `TASK-5--new.md` (committed on the branch), `chitty fix` leaves `TASK-5--old.md` byte-identical with the same `skipped: read from task-5` warning; `chitty fix chitty/tasks/<the no-branch ticket's file>` (a path filter that excludes `TASK-5`) lists no `TASK-5` warning
- [ ] In a linked worktree of `task-5` (`git branch task-5`, then `git worktree add <tmp>/task-5 task-5`; there commit a title change to `TASK-5`, then write `depends_on: [task-3]` into its `TASK-5` file uncommitted, and add an uncommitted malformed file `chitty/tasks/TASK-9--bad.md` containing `not frontmatter`), `chitty fix` run from that worktree repairs `TASK-5`'s file to `TASK-3`, lists `skipped: read from main` warnings for `main`'s tickets (these warnings fail before the change; the repair passes before and after), and reports `TASK-9--bad.md` as an error exactly as `fix` reports it on `main` today, leaving it unchanged
- [ ] In the main checkout, with local `task-7` and `origin/task-7` (made by `git update-ref`) at sibling commits, both ahead of `main` and each changing `TASK-7`, `chitty fix` exits 1 naming both; `make check` passes
- [ ] In the main checkout, with `chitty/tasks/TASK-6--a.md` and `chitty/tasks/TASK-6--b.md` (both `depends_on: [task-3]`, no `task-6` branch): `chitty fix` leaves both byte-identical and lists `skipped: TASK-6 is used by more than one file` for each, and `chitty check` still exits 1 reporting the duplicate. Record in a note what `fix` does there on `main` before the change; if it already leaves both files unchanged, the byte-identical part is a guard, and the warnings must fail before; `chitty fix chitty/tasks/TASK-6--a.md` lists only `TASK-6--a.md`'s warning and leaves both files byte-identical

## Notes

The duplicate-file requirement cannot be implemented as written: `Repo.find(id)` calls `lookup`, `source_copy`, and `_parse_source_copy`, which raises `ChittyError` whenever the selected source has more than one file. It does not resolve one working-tree file, so there is no first file to repair and second file to skip. Please decide whether duplicates should all be skipped or how an authoritative file is selected, and specify a regression fixture, action, and assertions for that choice (including the warning and `check` diagnostics). The ticket also requires path-filtered warnings and skipping a stale main filename absent from the selected branch, but describes no regression fixture, action, and assertions for either behavior; please specify those tests. No implementation was started and verification remains unfinished.

Planner 2026-11-21: decided duplicates are all skipped with a warning; `fix` no longer uses `Repo.find`. Added tests for the stale `main` filename, the path filter and duplicates (criteria 1 and 4).

Planner 2026-11-21, after the cold read: `source_of` parses nothing and gives short ref names; the duplicate count covers every scanned name regardless of `paths` or parsing; concrete worktree fixture for criterion 2; a filtered duplicate case.

## History

- 2026-11-18T16:38:05Z lively-quartz-crane → backlog
- 2026-11-18T16:39:35Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:39:35Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:51:22Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:51:22Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:51:24Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:55:48Z lively-quartz-crane: changed title, dependencies, description, acceptance criteria
- 2026-11-18T17:55:48Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:56:16Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:58:19Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:59:10Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:59:10Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:59:14Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:00:54Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:00:54Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:00:56Z lively-quartz-crane planning → todo
- 2026-11-21T13:05:19Z brisk-hazel-crane todo → doing
- 2026-11-21T13:07:18Z brisk-hazel-crane: changed owner, notes
- 2026-11-21T13:07:18Z brisk-hazel-crane doing → planning
- 2026-11-21T13:09:22Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
- 2026-11-21T13:09:22Z sunny-ebony-kestrel planning → cold-read
- 2026-11-21T13:11:27Z sunny-ebony-kestrel: changed description, acceptance criteria, notes
