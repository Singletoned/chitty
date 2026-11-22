---
title: Apply provisional renumbering as one store transaction
status: cold-read
depends_on:
  - TASK-391
  - TASK-507
  - TASK-519
  - TASK-520
parent: TASK-391
created: 2026-11-21
---

## Description

Apply the read-only plan from `TASK-391` through `Repo.renumber_provisional() -> tuple[Change, ...]` in `src/chitty/store.py`. This is store only; `TASK-392` wires up the CLI. The preflight `Repo._plan_provisional_renumbering() -> tuple[dict[TaskId, TaskId], tuple[StoredTask, ...]]` has landed with its guards (`TASK-391`, `TASK-519`, `TASK-520`, `TASK-536`); `rewrite_task` (`src/chitty/renumbering.py`), `Task.with_history_event`, `ids.filename`, `ids.slugify`, `_all_or_nothing`, `_prepare_write` and `_commit(change, verb)` exist (rechecked 2026-11-22). Split 2026-11-22: a failed commit is `TASK-542`, outside Git is `TASK-543`.

Call the preflight first; an empty plan returns `()` without `_prepare_write()`. Otherwise use `_prepare_write()` normally. Its own repository upgrade commit, if any, is outside the ticket transaction. For every writable ticket apply `rewrite_task` (`TASK-507`); preserve History and existing `moved_from` except that a renumbered ticket loses `provisional`, sets `moved_from` to its old ID, and appends a History event `renumbered from <old ID>` via `with_history_event`. Rewrite titles before computing paths. Keep each ticket in its original directory and derive every changed ticket's final path from `ids.filename` and `ids.slugify` of its final title, even when just the slug changes. Do not touch unchanged files, `_relocate` or `_save`.

Prepare the final tasks and paths in memory. In `_all_or_nothing`, `_write` each changed file once at the final path, remove superseded paths, and invalidate the store's caches before `_commit` so finalization can resolve newly written IDs. Use one `_commit` with all changed paths (including removals), `Task:` trailers for all changed tickets, and verb `renumber provisional tickets`, following the batch pattern in `archive_done`. Return one `Change` per renumbered ticket, not per reference-only rewrite; propagate errors, relying on existing rollback for files and index.

Use `tests/test_renumber_provisional.py`, `RepoTestCase`, real files and real Git initialized on `main` with local author and `autocommit = true`. Preflight has separate tests for allocation, source conflicts and invalid files. The transaction fixture commits a valid archived provisional `TASK-AAAAAA`, an active `TASK-BAAAAA` depending on it, and active `TASK-3` titled `After TASK-AAAAAA`, depending on `TASK-BAAAAA`, mentioning both old IDs and dangling numeric `TASK-4` in Description and mentioning an old ID in an existing History entry. Assert the new IDs are `TASK-5` and `TASK-6`, `TASK-3` is now `chitty/tasks/TASK-3--after-task-5.md`, dependencies and prose resolve to the new IDs except the dangling `TASK-4` prose, old paths are gone, both `moved_from` fields and new History events name their old IDs, and pre-existing History is unchanged (check entries, not formatter line wrapping). Cover the fixed real-files/commit/rollback cases rather than a new generated test: `TASK-507` covers the pure rewrite and `TASK-381` covers allocation. Demonstrate the regressions against a signature stub raising `NotImplementedError`, then verify with the new tests and `make check`.

## Acceptance Criteria

- [ ] The real-Git batch fixture returns one `Change` per renumbered ticket, updates both directories and all three tickets exactly as described, and lands one commit including every old and final path and a `Task:` trailer for each final ticket. Repeating returns `()` and changes neither HEAD nor bytes.
- [ ] `make check` passes

## Notes

The preflight is split across `TASK-391`, `TASK-519` (blocking structured references in untouched sources) and `TASK-520` (branch and invalid-input guards). Keep the writer waiting for the full contract.

## History

- 2026-11-21T18:33:02Z eager-ginger-adder → backlog
- 2026-11-21T18:37:17Z eager-ginger-adder: changed dependencies, description, acceptance criteria
- 2026-11-21T18:37:17Z eager-ginger-adder backlog → planning
- 2026-11-21T18:45:16Z eager-ginger-adder: changed dependencies, notes
- 2026-11-22T01:35:32Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T01:35:32Z lively-zinc-newt planning → cold-read
