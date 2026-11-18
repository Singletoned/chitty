---
title: Give new tickets a provisional ID off `main` through `Repo.new_id`
status: doing
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

- "Off `main`" means a Git checkout (`git.is_repository`) whose current branch is not the main branch (`Repo._main_branch()`), including a detached `HEAD`. A directory outside Git is never off `main`: it keeps sequential numbers. Off `main` while the configured main branch names no ref at all (neither `refs/heads/<main>` nor any `refs/remotes/*/<main>`; for example a repository on `master` with the default `main_branch`), `new_id` raises `ChittyError` naming the missing branch and `main_branch` in `chitty.toml`, rather than silently handing out provisional IDs for a configuration mistake. A single-branch clone with only `origin/main`, or a ticket branch, does not raise. An unborn `main` while on another branch raises too (a corner case; errors for now). Add a Git helper for this check that raises on Git failure, not `git.has_local_branch`, which swallows errors.
- New method `Repo.new_id(context) -> tuple[TaskId, bool]`, checked in this order: a context with `random_ids = true` gets a numeric random ID as today and `False`; off `main`, a provisional ID from `ids.provisional_suffix(_provisional_draw)` and `True`; otherwise `next_number` and `False`. `_provisional_draw(n)` is a module function in `src/chitty/store.py` returning `secrets.randbelow(n)`, the seam tests patch, like `_random_number`. A provisional ID already used by a ticket file in this checkout (active or archive directory of any context) is redrawn, up to `RANDOM_ID_ATTEMPTS`, then `ChittyError`: `no unused provisional ID in context <name> after <n> attempts`, as the random-ID message reads.
- `Repo.add`, `Repo.move` and `Repo.renumber` get new IDs only from `new_id`, and set the ticket's `provisional` field from its boolean (`True`, or `None` to remove it). So `move` or `renumber` on `main` of a provisional ticket gives a sequential ID and clears the field. `renumber` sets the field on the task it passes to `_relocate`, which only sets `moved_from`. `Inbox` pulls (`src/chitty/inbox.py`) go through `add`, so off `main` they get provisional IDs too: intended.
- Remove the rule in `resolve_add_target` filing plain `add` in a linked worktree into `backlog`: with no `-c`, `add` uses `default_context` everywhere. MCP `add` goes through the same function.
- Update every test that expects a plain `add` in a worktree, on a non-`main` branch, or in a repository on `master` (under `RepoTestCase`'s isolated `HOME`, `git init` makes `master`) to use `git init -b main` or expect a provisional ID or the default context. Known cases from a cold read that ran the suite: `tests/test_backlog_context.py` (`test_plain_add_in_a_linked_worktree_uses_backlog`, including its `-c human` line); `tests/test_mcp.py` (`test_plain_add_in_a_linked_worktree_uses_backlog`); `tests/test_autocommit.py` (`test_linked_worktree_write_does_not_upgrade_setup`, `test_linked_worktree_write_with_stale_setup_succeeds_without_autocommit`); `tests/test_check_cross_branch_references.py` (the "other branch" case of `test_reference_existence_matches_show`); `tests/test_property_refused_write.py` (`setUp`); `tests/test_cli.py` (`TestInit.test_stale_writes_warn_and_skip_damaged_guide_upgrade`); `tests/test_store.py` (`test_numbers_count_committed_tasks_on_another_branch`: commit its numeric file on `other` directly with Git, since `add` there is now provisional). The guides, README and docs, and `tests/test_cli.py` `test_branch_discoveries_are_filed_in_backlog`, which pins guide wording, are `TASK-390`'s; this ticket changes no guide text. `next_number` itself is unchanged here (`TASK-379`).
- Label `needs-minor`: plain `add` in a worktree changes context and ID form.

Tests: real-Git tests through the CLI in a new `tests/test_provisional_ids.py`, inheriting `CliTestCase` from `tests/test_cli.py` (for `run_cli`) and running `git init -b main` itself (`git init -b master` for the `master` case). Add a `backlog` context (`prefix = "BACKLOG"`, `random_ids = true`) to the test's `chitty.toml`: the `RepoTestCase` fixture has only `tasks` and `human`. Provisional tickets are referred to by full ID (`TASK-K7Q2M`): bare suffixes do not resolve. No property: a fixed set of checkout states (main, linked worktree on a branch, main checkout switched to a branch, detached `HEAD`, outside Git) and commands (`add`, `move`, `renumber`), each listed in the criteria and tested.

## Acceptance Criteria

- [ ] Plain `chitty add` (no `-c`) in a linked worktree on branch `feature`, in the main checkout switched to `feature`, and on a detached `HEAD` each creates a ticket in `default_context` whose ID suffix contains a letter and whose file has `provisional: true`; the linked-worktree case fails before the change
- [ ] Plain `chitty add` on `main` and in a directory outside Git gives the next sequential number with no `provisional` key; `chitty add -c backlog` on `feature` still gives a numeric random ID with no `provisional` key; in a repository on `master` with the default `main_branch`, `chitty add` fails naming `main` and `main_branch` and creates no file
- [ ] `chitty move TASK-1 human` on `feature` (`TASK-1` in `tasks`) gives a provisional `HUMAN-` ID with `provisional: true`; after `git merge feature` into `main`, `chitty move <that ID> tasks` in the main checkout gives a sequential `TASK-` ID and removes the key; `chitty renumber` of a provisional file copied under another slug on `main` (as `tests/test_renumber.py` builds duplicates) gives a sequential ID and removes the key
- [ ] With `_provisional_draw` patched to return 0 for its first six calls and 1 after, and `TASK-AAAAAA` present, `chitty add` on `feature` gets `TASK-BBBBBB`; patched to always return 0 with `TASK-AAAAAA` present, it exits 1 with `no unused provisional ID`; with only `origin/main` (no local `main`) on a ticket branch, `chitty add` gives a provisional ID; `make check` passes

## History

- 2026-11-18T16:28:10Z lively-quartz-crane → backlog
- 2026-11-18T16:28:38Z lively-quartz-crane: changed labels, dependencies, description, acceptance criteria
- 2026-11-18T16:28:38Z lively-quartz-crane backlog → planning
- 2026-11-18T16:29:27Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:41:13Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:41:13Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:41:15Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:45:30Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:45:30Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:45:32Z lively-quartz-crane planning → todo
- 2026-11-18T17:45:40Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T22:25:25Z eager-ebony-newt todo → doing
