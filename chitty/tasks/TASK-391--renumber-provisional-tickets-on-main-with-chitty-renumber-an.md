---
title: Renumber provisional tickets on `main` with `chitty renumber` and no path
status: cold-read
depends_on:
  - TASK-381
  - TASK-389
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` and `provisional: true` (`TASK-380`, `TASK-389`). Once it reaches `main` it should get an ordinary sequential number. This is cosmetic: provisional IDs work everywhere, so renumbering is one idempotent command a person or script can run at any time.

Starts after `TASK-381` (`plan_renumbering`, `replace_ids`) and `TASK-389` land.

Decisions:

- `chitty renumber` with no `PATH` calls a new `Repo.renumber_provisional()`. `PATH` becomes optional; `chitty renumber PATH`, its `--json` keys (`renumbered_dict`, pinned by `tests/test_renumber.py`) and the existing MCP `renumber(path)` tool are unchanged. No new MCP tool.
- "On `main`" means a Git checkout whose current branch is the main branch, or a directory outside Git (never off `main`, as in `TASK-389`). Off `main` it changes nothing, prints `provisional tickets are renumbered on main; nothing changed`, and exits 0.
- It works on this checkout's ticket files on disk (active and archive directories of every context), not on `all_tasks()`: a ticket read from another ref must not be written, and tickets only on other branches are not touched (their mentions then dangle; accepted).
- Extract `Repo._used_numbers(context) -> set[int]` from `next_number`, which then returns `ids.next_number` of it; pass those sets to `plan_renumbering`. A provisional ticket in a `random_ids` context is skipped with a printed warning naming it.
- For each renumbered ticket: rename the file (same slug) to the new ID, remove `provisional`, set `moved_from` to the provisional ID (replacing any earlier value), and add a History event `renumbered from <old ID>`.
- Rewrite mentions with `replace_ids` in every ticket file on disk: in `depends_on` and `parent`, and in every body section except `History`, which is append-only. A renumbered file's own `moved_from` and History keep the provisional ID.
- Order: `_prepare_write()` first; write the renamed files, then the rewrites (with `_write`, so `depends_on` checks see the new files); then one `_commit(change, "renumber provisional tickets")`, as `archive_done` does. Snapshot the ticket files with `_task_file_bytes` before writing and restore them with `_restore_task_files` on any error, so a failed run leaves `git status` as it was.
- With no provisional ticket it writes nothing, makes no commit, prints `nothing to renumber`, and exits 0. `--json` prints a list of renumbered tickets, as `archive` with no ID does, and `[]` when there are none.
- Update the `renumber` help in `src/chitty/cli.py` and `docs/plan/cli.md`.

Tests: real-file CLI tests in a new `tests/test_renumber_provisional.py`, inheriting `RepoTestCase` from `tests/support.py`, running `git init` and setting `autocommit = true`. Make provisional tickets with `chitty add` on a branch (archive one there), then `git merge` the branch into `main` so every referencing ticket is on `main`. No property beyond `TASK-381`'s: the Repo side is file plumbing over a fixed set of cases, each in the criteria.

## Acceptance Criteria

- [ ] On `main`, with `TASK-3` the highest number, an active and an archived provisional ticket, and a third ticket listing one in `depends_on` and mentioning both in its Description: `chitty renumber` gives them `TASK-4` and `TASK-5` in sorted `TaskId` order, renames both files, removes `provisional`, sets `moved_from` to each provisional ID, rewrites the third ticket's `depends_on` and Description but not its History, and makes one commit
- [ ] Running `chitty renumber` again prints `nothing to renumber`, makes no commit and exits 0; off `main` it prints `provisional tickets are renumbered on main; nothing changed`, changes no file and exits 0
- [ ] When the run fails after writing (for example a ticket file that fails to parse is planted), `git status` is unchanged afterwards; a ticket existing only on another branch that mentions a provisional ID does not stop the run and is left unchanged on that branch
- [ ] `chitty renumber --json` prints a list (`[]` when nothing changes); `chitty renumber PATH` for two files sharing an ID and the MCP `renumber` tool behave as before; `make check` passes

## History

- 2026-11-18T16:34:15Z lively-quartz-crane → backlog
- 2026-11-18T16:34:50Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:34:50Z lively-quartz-crane backlog → planning
- 2026-11-18T16:35:13Z lively-quartz-crane planning → cold-read
