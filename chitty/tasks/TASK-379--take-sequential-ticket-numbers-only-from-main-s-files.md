---
title: Take sequential ticket numbers only from main's files
status: cold-read
depends_on:
  - TASK-389
parent: TASK-376
created: 2026-11-18
---

## Description

Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), only `main` hands out sequential ticket numbers; everywhere else new tickets get provisional IDs (`TASK-389`). So the next number needs only `main`'s own ticket files. Today `Repo.next_number` in `src/chitty/store.py` also reads every local and remote-tracking ref's history (`self._history()`, from `git.historical_files`), which is slow, conflicts with work in containers that cannot see every branch, and is the last reason except reads (`TASK-378`) to keep that scan.

Starts after `TASK-389` lands: `Repo.new_id` does not exist yet.

Decisions:

- `Repo.next_number(context)` counts only the ticket files in this checkout's active and archive directories of that context (committed or not), plus `_deleted_numbers` when `archive = "delete"`, as today. Remove its loop over `self._history()`. Leave `_history()` and `git.historical_files` in place for the reads; `TASK-386` deletes them.
- Order inside `next_number`: the `random_ids` branch first, then the off-`main` check, then the sequential number.
- For a sequential context, `next_number` raises `ChittyError` when the checkout is off `main` as `TASK-389` defines it (inside Git, current branch not the main branch, including detached `HEAD`); outside Git it never raises. After `TASK-389`, `Repo.new_id` never calls it there, so a call off `main` is a bug that must not hand out a clashing number. Only a direct call can reach it, so the test calls `Repo.next_number` directly.
- Contexts with `random_ids = true` now avoid only numbers in this checkout's files, not those on other branches: a clash among 90 million numbers is accepted. Update `tests/test_backlog_context.py` `test_retries_a_number_used_only_on_another_branch` to that narrower rule (a number used in this checkout is still skipped).
- Out of scope: `_deleted_numbers` (it reads `git log --all` and already refuses a shallow clone; leave it, so delete mode still counts numbers deleted on any branch and does not work in a shallow container), and renumbering (`TASK-391`).
- Replace the `n is unpadded` bullet in `docs/plan/ids.md` with: "`n` is unpadded: one above the highest number in the ticket files of the main checkout, active or archived, committed or not (with `archive = \"delete\"`, also numbers deleted on any branch). Only `main` hands out sequential numbers; elsewhere new tickets get provisional IDs."

Tests: real-Git tests in a new `tests/test_next_number_main.py`, inheriting `CliTestCase` from `tests/test_cli.py`, with `git init -b main`. Make `feature` with a committed `TASK-50` file, and `origin/other` with `git update-ref refs/remotes/origin/other <commit>` of a commit adding `TASK-60`. No property: a fixed set of places a number can live (committed on `main`, uncommitted in the main checkout, archived, on another local branch, on a remote-tracking branch), each listed in the criteria and tested.

## Acceptance Criteria

- [ ] On `main` with `TASK-3` its highest ticket, a local branch `feature` with a committed `TASK-50` and a remote-tracking branch `origin/other` with a committed `TASK-60` (neither on `main`): `chitty add` gives `TASK-4`; the test fails before the change
- [ ] Regression guard (passes before too): an uncommitted new `TASK-7` in the main checkout and an archived `TASK-9` on `main` are counted: `chitty add` gives `TASK-10`
- [ ] A direct `Repo.next_number` call for a sequential context raises `ChittyError` in a linked worktree on `feature`, in the main checkout switched to `feature`, and on a detached `HEAD`, and returns a number outside Git; the linked-worktree case fails before the change
- [ ] `docs/plan/ids.md` has the replacement bullet from the Description; `tests/test_backlog_context.py` follows the narrower random-ID rule; `make check` passes

## History

- 2026-11-18T16:20:05Z lively-quartz-crane → backlog
- 2026-11-18T16:20:29Z lively-quartz-crane: changed title
- 2026-11-18T16:23:18Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:27:09Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:27:09Z lively-quartz-crane backlog → planning
- 2026-11-18T16:28:40Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T16:40:30Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:43:04Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:43:04Z lively-quartz-crane cold-read → planning
- 2026-11-18T16:43:06Z lively-quartz-crane planning → cold-read
