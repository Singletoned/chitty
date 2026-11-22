---
title: Choose the message for a refused ticket write in a pure function
status: cold-read
parent: TASK-385
created: 2026-11-22
---

## Description

Split from `TASK-385` on 2026-11-22 so each part fits one worker session. `TASK-385` replaces `Repo._require_current_version` with a guard that refuses a ticket write only when the ticket is read from somewhere other than this checkout's working tree, with a message saying where to make the edit. This ticket adds only the pure function that chooses that message; nothing calls it yet.

Add to a new module `src/chitty/write_guard.py` (no imports from `chitty.store` or `chitty.run`):

`write_refusal(task_id: str, source: str | None, main_branch: str, local_branch: bool, worktree: Path | None, main_checkout: Path | None, checkout_is_main: bool, local_behind: bool) -> str | None`

- `source` is `StoredTask.branch`: `None` means read from this checkout's working tree.
- `local_branch` says whether `source` names a local branch; `worktree` is the worktree that has `source` checked out, if any; `main_checkout` is the main checkout's path; `checkout_is_main` says whether the current checkout is the main checkout; `local_behind` says, for a remote-tracking `source`, whether a local branch of the same name exists (behind it).

Rules, in order (from `TASK-385`'s owner-approved decisions):

1. `source is None`: return `None` (the write is allowed).
2. `source == main_branch`: if `checkout_is_main`, return `f"{task_id} is read from {main_branch}; switch this checkout to {main_branch} first"`; else `f"{task_id} is read from {main_branch}; edit it in the main checkout {main_checkout}"`.
3. `local_branch`: if `worktree` is not `None`, `f"{task_id} is in flight on branch {source}; edit it in worktree {worktree}"`; else `f"{task_id} is in flight on branch {source}; run git switch {source} first"`.
4. Otherwise `source` is a remote-tracking name `<remote>/<b>` (split at the first `/`): if `local_behind`, `f"{task_id} is in flight on {source}; fast-forward {b} to {source} first"`; else `f"{task_id} is in flight on {source}; run git switch --track {source} first"`.

Tests: Hypothesis (the repository's property tool) in a new `tests/test_property_write_guard.py`. Draw a ticket ID, a main branch name, a source (none, the main name, a local name `task-<n>`, or `<remote>/task-<n>`), and the flags and paths. Expected message computed from the drawn values by the rules above, written out in the test; assert `write_refusal` returns it. Also one example per rule with literal strings. Before implementing, add the function raising `NotImplementedError` and confirm the tests fail.

## Acceptance Criteria

- [ ] The property and the per-rule examples pass, and fail against a `NotImplementedError` stub; `make check` passes

## History

- 2026-11-22T02:28:29Z lively-zinc-newt → cold-read
- 2026-11-22T02:28:39Z lively-zinc-newt: changed description
