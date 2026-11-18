---
title: Renumber provisional tickets in `Repo.renumber_provisional`
status: planning
depends_on:
  - TASK-381
  - TASK-389
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket created off `main` gets a provisional ID such as `TASK-K7Q2MX` and `provisional: true` (`TASK-380`, `TASK-389`). Once it reaches `main` it should get an ordinary sequential number. This is cosmetic and idempotent. This ticket builds the store method; `TASK-392` wires it to the CLI.

Starts after `TASK-381` (`plan_renumbering`, `replace_ids`) and `TASK-389` land.

Decisions:

- New `Repo.renumber_provisional() -> tuple[Change, ...]` in `src/chitty/store.py`, returning one `Change` per renumbered ticket (empty when none).
- It acts only "on `main`": outside a Git repository (`git.is_repository` false), or in one whose current branch is the main branch. Off `main`, including a detached `HEAD`, it raises `ChittyError` saying provisional tickets are renumbered on main; the CLI turns that into a no-op (`TASK-392`).
- It works on this checkout's ticket files on disk (active and archive directories of every context), not on `all_tasks()`: a ticket read from another ref must not be written, and tickets only on other branches are not touched (their mentions then dangle; accepted).
- First parse every ticket file and plan everything (`plan_renumbering`), so an unparseable file fails before any write.
- Extract `Repo._used_numbers(context) -> set[int]` from `next_number`, keeping everything `next_number` counts (active and archive files, and `_deleted_numbers` in delete mode); `next_number` then returns `ids.next_number` of it for sequential contexts, its random branch unchanged. Pass those sets to `plan_renumbering`. A provisional ticket in a `random_ids` context is left alone.
- For each renumbered ticket: a new helper (do not change `_relocate`, which `move` and `renumber PATH` share) renames the file to the new ID with the same slug, removes `provisional`, sets `moved_from` to the provisional ID (replacing any earlier value), and adds a History event `renumbered from <old ID>`.
- Rewrite mentions with `replace_ids` in every ticket file on disk: in `depends_on` and `parent`, and in every body section except `History`, which is append-only. A renumbered file's own `moved_from` and History keep the provisional ID.
- Order: `_prepare_write()` first; snapshot ticket files with `_task_file_bytes`; write the renamed files, then the rewrites (with `_write`, so dependency checks see the new files); then one `_commit(change, "renumber provisional tickets")` whose `Task:` trailers name every renamed and rewritten ticket, as `archive_done` batches. On any error after the snapshot (including `chitty fix` validation, formatting or a failed autocommit inside `_commit`), restore with `_restore_task_files` and the index, as `Repo.edit` does, then re-raise.

Tests: real-file tests calling `Repo.renumber_provisional()` in a new `tests/test_renumber_provisional.py`, inheriting `RepoTestCase` from `tests/support.py`, running `git init` and setting `autocommit = true` (its default config has `autocommit = false`). Patch the provisional draw (`_provisional_draw`, `TASK-389`) so suffixes are known. Make provisional tickets with `chitty add` on a branch (archive one there), `git switch main`, `git merge` the branch, and stay on `main`. No property beyond `TASK-381`'s: file plumbing over the cases in the criteria.

## History

- 2026-11-18T16:34:15Z lively-quartz-crane → backlog
- 2026-11-18T16:34:50Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:34:50Z lively-quartz-crane backlog → planning
- 2026-11-18T16:35:13Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:37:35Z lively-quartz-crane: changed title, description, acceptance criteria
- 2026-11-18T16:37:35Z lively-quartz-crane cold-read → planning
