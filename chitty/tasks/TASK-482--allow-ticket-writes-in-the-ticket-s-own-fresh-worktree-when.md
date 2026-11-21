---
title: Allow ticket writes in the ticket's own fresh worktree when `main` holds its copy
status: doing
parent: TASK-376
created: 2026-11-21
---

## Description

Split out of `TASK-378` on 2026-11-21, when its worker found the whole read switch too large for one session. After `TASK-378`, a ticket in a fresh ticket worktree (its branch `task-6` made at `main`'s tip, with no commit of its own yet) is read from `main`, because `main`'s copy is authoritative until the branch changes it. `Repo._require_current_version` (`src/chitty/store.py`) refuses a write when `stored.branch` is neither `None` nor the current branch, so the first write in such a worktree, including the runner's claim on the branch (`TASK-384`), would be refused. This ticket adds the allowance first. Under today's reads it only adds a case where a write is allowed, so nothing that works today stops working.

Decision (owner, 2026-11-20): `_require_current_version` also returns without raising when all of these hold: the current branch is the ticket's own branch (`str(stored.id).lower()`, so `task-6` for `TASK-6`); `stored.branch` is the configured main branch; and `git.changed_since_split(self.root, f"refs/heads/{main}", f"refs/heads/{own}", paths)` (`src/chitty/git.py`) is false, where `paths` is the union of the paths (the first element of each `(path, content)` pair) returned by `self._ref_ticket_files(ref, stored.id)` for those two refs; `<main>` is `self._main_branch()`. The write then commits on the branch, which puts the branch ahead of `main`, so every checkout reads the ticket from the branch afterwards. A branch merged into `main` that `main` has changed since is still refused. Every other case is refused as today; `TASK-385` replaces the guard later.

Tests: real Git, in a new `tests/test_own_worktree_writes.py` with a class inheriting `CliTestCase` from `tests/test_cli.py`, set up with `git init -b main` and `autocommit = true` as `tests/test_check_cross_branch_references.py` does. The linked worktree is made with `git worktree add -b task-6 <dir> main` after `TASK-6` is committed on `main`; the CLI runs with that directory as the working directory. The direct tests open `Repo.open(<worktree>)` and build the `StoredTask` with the given `branch` and the ticket's real path and parsed task (read from the file). `main` gets its post-split commit from the main checkout, which stays on `main`; the merge is `git merge --ff-only task-6` run in the main checkout. The `feature` checkout is another linked worktree, `git worktree add -b feature <dir> main`. The failing CLI case passes `exit_code=1` to `run_cli`. Alphanumeric ticket IDs are out of scope here; the rule only lower-cases `str(stored.id)`. No property: a fixed set of branch relations, each in the criteria.

## Acceptance Criteria

- [ ] In the linked worktree of a fresh `task-6` made at `main`'s tip, `chitty edit TASK-6 --note x` succeeds and commits on `task-6`; after `task-6` is fast-forward merged into `main` and a further `main` commit changes `TASK-6`, the same edit in that worktree exits 1 with the `_require_current_version` message naming `main` and makes no commit (the first edit fails before the change, refused by `_require_current_version`; the refusal after the merge passes before too)
- [ ] Direct tests of `Repo._require_current_version` with a `StoredTask` whose `branch` is `main`, from a checkout on branch `task-6`: it returns when `main` has not changed `TASK-6`'s files since `task-6` split from it (only `main`'s side matters: had the branch changed them, the ticket would be read from `task-6`, which is allowed today); it raises when `main` changed them since the split; it raises with `stored.branch` set to `feature` from `task-6` while `TASK-6` is unchanged; it raises from a checkout on branch `feature` (each against a real Git repository; the first fails before the change)
- [ ] `make check` passes

## Plan

Add real-Git linked-worktree regression tests for CLI writes and direct guard branch relationships, confirm the new allowances fail before the fix, then implement the specified main-side path comparison and run the full checks.

## Notes

Criterion 1 says the first fresh-worktree CLI edit fails before this change, but the specified real-Git test passes both before and after the main-side change without any implementation fix. Current single-ticket reads still use the old history-based lookup; TASK-378, which depends on this ticket, switches them to source_copy. Therefore the CLI regression cannot prove this guard change before TASK-378, and the criterion's required pre-fix failure is currently impossible. Planning needs to decide how to split or revise the CLI regression and its evidence without introducing a dependency cycle. The direct unchanged-main guard test does fail before the fix with the expected branch-main error; the other direct guard cases pass. Partial tests are committed in cf35be2f, with the direct regression intentionally failing. make check passed formatting, lint and pyright but timed out after 120 seconds during unittest; the targeted unittest run confirms one error and four passes. No implementation fix was made.

## History

- 2026-11-21T01:20:56Z quick-pearl-lapwing → planning
- 2026-11-21T01:23:37Z quick-pearl-lapwing planning → cold-read
- 2026-11-21T01:24:40Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-21T01:24:40Z quick-pearl-lapwing cold-read → todo
- 2026-11-21T01:25:07Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-21T01:25:34Z intrepid-yellow-heron todo → doing
- 2026-11-21T01:28:49Z intrepid-yellow-heron: wrote the plan
- 2026-11-21T01:32:17Z intrepid-yellow-heron: changed notes
