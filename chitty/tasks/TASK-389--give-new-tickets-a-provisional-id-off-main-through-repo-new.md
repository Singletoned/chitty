---
title: Give new tickets a provisional ID off `main` through `Repo.new_id`
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-380
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), only `main` hands out sequential ticket numbers. A ticket created anywhere else gets a provisional ID marked `provisional: true`. `TASK-381` renumbers them on `main` later, and provisional IDs must work everywhere until then.

Today plain `chitty add` in a linked worktree files the ticket in the `backlog` context with a numeric random ID (`resolve_add_target` in `src/chitty/store.py`), and every other new ID on a branch is sequential (`Repo.next_number`).

Starts after `TASK-380` lands: `ids.provisional_suffix` and the `provisional` field do not exist yet.

Decisions:

- "Off `main`" means a Git checkout (`git.is_repository`) whose current branch is not the main branch (`Repo._main_branch()`), including a detached `HEAD`. A directory outside Git is never off `main`: it keeps sequential numbers.
- New method `Repo.new_id(context) -> tuple[TaskId, bool]`, checked in this order: a context with `random_ids = true` gets a numeric random ID as today and `False`; off `main`, a provisional ID from `ids.provisional_suffix(_provisional_draw)` and `True`; otherwise `next_number` and `False`. `_provisional_draw(n)` is a module function in `src/chitty/store.py` returning `secrets.randbelow(n)`, the seam tests patch, like `_random_number`. A provisional ID already used by a ticket file in this checkout (active or archive directory of any context) is redrawn, up to `RANDOM_ID_ATTEMPTS`, then `ChittyError`.
- `Repo.add`, `Repo.move` and `Repo.renumber` get new IDs only from `new_id`, and set the ticket's `provisional` field from its boolean (`True`, or `None` to remove it). So `move` or `renumber` on `main` of a provisional ticket gives a sequential ID and clears the field.
- Remove the rule in `resolve_add_target` filing plain `add` in a linked worktree into `backlog`: with no `-c`, `add` uses `default_context` everywhere. MCP `add` goes through the same function.
- Update `tests/test_backlog_context.py` (the linked-worktree case) and `tests/test_store.py` `test_numbers_count_committed_tasks_on_another_branch`, which adds from a linked worktree and now gets provisional IDs. The guides, README and docs are `TASK-390`.
- Label `needs-minor`: plain `add` in a worktree changes context and ID form.

Tests: real-Git tests through the CLI in a new `tests/test_provisional_ids.py`, inheriting `RepoTestCase` from `tests/support.py` and running `git init` itself. Provisional tickets are referred to by full ID (`TASK-K7Q2M`): bare suffixes do not resolve. No property: a fixed set of checkout states (main, linked worktree on a branch, main checkout switched to a branch, detached `HEAD`, outside Git) and commands (`add`, `move`, `renumber`), each listed in the criteria and tested.

## Acceptance Criteria

- [ ] Plain `chitty add` (no `-c`) in a linked worktree on branch `feature`, in the main checkout switched to `feature`, and on a detached `HEAD` each creates a ticket in `default_context` whose ID suffix contains a letter and whose file has `provisional: true`; the linked-worktree case fails before the change
- [ ] Plain `chitty add` on `main` and in a directory outside Git gives the next sequential number with no `provisional` key, and `chitty add -c backlog` on `feature` still gives a numeric random ID with no `provisional` key
- [ ] `chitty move` to another context on `feature` gives a provisional ID with `provisional: true`; after `git merge feature` into `main`, `chitty move` of that ticket in the main checkout gives a sequential ID and removes the key, and `chitty renumber` of a provisional file that shares its ID with another file on `main` does the same
- [ ] With `_provisional_draw` patched so the first suffix equals an existing ticket's, `chitty add` on `feature` gets a different ID; when every draw clashes it fails with `ChittyError` after `RANDOM_ID_ATTEMPTS`; `make check` passes

## History

- 2026-11-18T16:28:10Z lively-quartz-crane → backlog
- 2026-11-18T16:28:38Z lively-quartz-crane: changed labels, dependencies, description, acceptance criteria
- 2026-11-18T16:28:38Z lively-quartz-crane backlog → planning
