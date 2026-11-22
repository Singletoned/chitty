---
title: Apply provisional renumbering as one store transaction
status: doing
depends_on:
  - TASK-391
  - TASK-507
  - TASK-519
  - TASK-520
  - TASK-544
parent: TASK-391
created: 2026-11-21
---

## Description

Apply the read-only plan from `TASK-391` through `Repo.renumber_provisional() -> tuple[Change, ...]` in `src/chitty/store.py`. This is store only; `TASK-392` wires up the CLI. The preflight `Repo._plan_provisional_renumbering() -> tuple[dict[TaskId, TaskId], tuple[StoredTask, ...]]` has landed with its guards (`TASK-391`, `TASK-519`, `TASK-520`, `TASK-536`); `rewrite_task` (`src/chitty/renumbering.py`), `Task.with_history_event`, `ids.filename`, `ids.slugify`, `_all_or_nothing`, `_prepare_write` and `_commit(change, verb)` exist (rechecked 2026-11-22). Split 2026-11-22: a failed commit is `TASK-542`, outside Git is `TASK-543`.

Call the preflight first; an empty plan returns `()` without `_prepare_write()`. Otherwise use `_prepare_write()` normally. Its own repository upgrade commit, if any, is outside the ticket transaction. Use `Repo._prepare_renumbering(mapping, writable) -> list[tuple[StoredTask, Task, Path]]` (`TASK-544`, landed 2026-11-22) for the final tasks and paths, and its test fixture in `tests/test_renumber_provisional.py`. (Its rules, for reference: for every writable ticket apply `rewrite_task` (`TASK-507`); preserve History and existing `moved_from` except that a renumbered ticket loses `provisional`, sets `moved_from` to its old ID, and appends a History event `renumbered from <old ID>` via `with_history_event`. Rewrite titles before computing paths. Keep each ticket in its original directory and derive every changed ticket's final path from `ids.filename` and `ids.slugify` of its final title, even when just the slug changes. Do not touch unchanged files, `_relocate` or `_save`.) This ticket writes them: `Task:` trailers go on every changed ticket, including reference-only ones such as `TASK-3`, as `archive_done` puts all changed tasks in its `Change`. The repeat check runs on `main` (off `main` the preflight raises `ProvisionalOffMain` first). The fixture is `TASK-544`'s (with `TASK-BAAAAA` provisional and an untouched `HUMAN-1` whose bytes must not change); reuse it.

Prepare the final tasks and paths in memory. In `_all_or_nothing`, `_write` each changed file once at the final path, remove superseded paths, and invalidate the store's caches before `_commit` so finalization can resolve newly written IDs. Use one `_commit` with all changed paths (including removals), `Task:` trailers for all changed tickets, and verb `renumber provisional tickets`, following the batch pattern in `archive_done`. Return one `Change` per renumbered ticket, not per reference-only rewrite; propagate errors, relying on existing rollback for files and index.

Use `tests/test_renumber_provisional.py`, `RepoTestCase`, real files and real Git initialized on `main` with local author and `autocommit = true`. Preflight has separate tests for allocation, source conflicts and invalid files. The transaction fixture commits a valid archived provisional `TASK-AAAAAA`, an active `TASK-BAAAAA` depending on it, and active `TASK-3` titled `After TASK-AAAAAA`, depending on `TASK-BAAAAA`, mentioning both old IDs and dangling numeric `TASK-4` in Description and mentioning an old ID in an existing History entry. Assert the new IDs are `TASK-5` and `TASK-6`, `TASK-3` is now `chitty/tasks/TASK-3--after-task-5.md`, dependencies and prose resolve to the new IDs except the dangling `TASK-4` prose, old paths are gone, both `moved_from` fields and new History events name their old IDs, and pre-existing History is unchanged (check entries, not formatter line wrapping). Cover the fixed real-files and commit cases rather than a new generated test: `TASK-507` covers the pure rewrite and `TASK-381` covers allocation. Demonstrate the regressions against a signature stub raising `NotImplementedError`, then verify with the new tests and `make check`.

Exact steps (from a cold reader's probe on `main` 2026-11-22, which ran this sequence and got one commit, three `Task:` trailers and an empty repeat):

1. Add `renumber_provisional(self) -> tuple[Change, ...]` to `Repo` next to `archive_done`: `mapping, writable = self._plan_provisional_renumbering()`; if `mapping` is empty return `()` before `_prepare_write()`; then `self._prepare_write()`; `prepared = self._prepare_renumbering(mapping, writable)`.
2. In `with self._all_or_nothing():` `_write` every final file at its final path; unlink each original path that differs from its final path; call `self._invalidate()` after the last unlink (reviewer-checked; no test can see it); build `final_tasks` as `StoredTask(final_id, original.context, final_path, original.archived, final_task)` for every prepared entry; call `self._commit(Change(first_renumbered, paths, final_tasks), "renumber provisional tickets")`, where `first_renumbered` is the final entry of the first renumbered ticket in `prepared` order (so the subject names a renumbered ticket) and `paths` holds every final and removed path. This one combined `Change` gives every changed ticket, including reference-only `TASK-3`, a `Task:` trailer.
3. Return one `Change` per renumbered ticket only (here `TASK-5` and `TASK-6`), not the combined one.

Test, in `tests/test_renumber_provisional.py`, reusing `TestPrepareRenumbering`'s fixture and its `CHITTY_ACTOR` patch, with `chitty.toml` rewritten to `autocommit = true` after `RepoTestCase.setUp` and committed: assert two `Change`s are returned; `git rev-list --count HEAD` rises by exactly 1; `git show --name-status HEAD` lists both old paths as deleted and every final path; the commit message has `Task: TASK-3`, `Task: TASK-5` and `Task: TASK-6`; the final files match what `_prepare_renumbering` produced; and a second call returns `()` with HEAD and every file's bytes unchanged.

## Acceptance Criteria

- [ ] The real-Git batch fixture returns one `Change` per renumbered ticket, updates both directories and all three tickets exactly as described, and lands one commit including every old and final path and a `Task:` trailer for each final ticket. Repeating returns `()` and changes neither HEAD nor bytes.
- [ ] `make check` passes

## Plan

Reuse the prepared fixture to test a real Git batch and repeat, then implement the transactional writer and run the full checks.

## Notes

The preflight is split across `TASK-391`, `TASK-519` (blocking structured references in untouched sources) and `TASK-520` (branch and invalid-input guards). Keep the writer waiting for the full contract.

Split again 2026-11-22 after a cold read: the in-memory prepare step is `TASK-544`. Keep in planning until it lands, then cold-read.

## History

- 2026-11-21T18:33:02Z eager-ginger-adder → backlog
- 2026-11-21T18:37:17Z eager-ginger-adder: changed dependencies, description, acceptance criteria
- 2026-11-21T18:37:17Z eager-ginger-adder backlog → planning
- 2026-11-21T18:45:16Z eager-ginger-adder: changed dependencies, notes
- 2026-11-22T01:35:32Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T01:35:32Z lively-zinc-newt planning → cold-read
- 2026-11-22T01:38:03Z lively-zinc-newt: changed dependencies, description, notes
- 2026-11-22T01:38:03Z lively-zinc-newt cold-read → planning
- 2026-11-22T03:02:07Z lively-zinc-newt: changed description
- 2026-11-22T03:02:07Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:04:02Z lively-zinc-newt: changed description
- 2026-11-22T03:04:02Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:04:32Z upbeat-bronze-newt todo → doing
- 2026-11-22T03:07:07Z upbeat-bronze-newt: wrote the plan
