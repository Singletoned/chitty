---
title: Merge and check around reviews in `chitty run`, fast-forwarding `main` after a pass
status: todo
priority: high
depends_on:
  - TASK-126
created: 2026-11-03
---

## Description

Merging is mechanical and has gone wrong. The global `chitty` is an editable install of the main checkout, so a conflicted merge there leaves conflict markers in `src/chitty/*.py` and breaks `chitty` in every repository until it is resolved (`TASK-118`). `TASK-104` also spent a full review to learn that its branch would not merge. Have `chitty run` do it, around the review:

Before starting a review session:

1. Merge `main` into the ticket's branch in its worktree. On a conflict, abort the merge and move the ticket to `doing` with the note `Review failed (integration): ...` naming the conflicting files.
2. Run the new `check` command from `chitty.toml` in the worktree, parsed without a shell like `autoformat`, and with no default for the same reason as `setup`. On failure, move the ticket to `doing` with `Review failed (work): ...` and the end of the output. Set `check = "make check"` in this repository.
3. In both cases, do not start Pi: no review is spent on work that cannot pass, and `chitty run` exits 0 because the status changed.

The reviewer therefore sees exactly what will land.

After a session that moves the ticket to `done`:

4. Fast-forward `main` to the branch from the main checkout, with `git merge --ff-only`, then remove the worktree and branch. If `main` has moved or the main checkout is dirty, leave everything in place and exit non-zero with a message: never resolve anything in the main checkout. Running `chitty run` again repeats the merge for a `done` ticket that still has a branch, before choosing the next ticket.

These automatic failures count towards `REVIEW_FAILURE_LIMIT` like any other `review → doing`.

The Pi review prompt stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to merge `main` into the branch in the worktree first, then only fast-forward `main`.

Out of scope: pushing, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests with a fake `pi` and a real Git repository cover a clean merge, a conflict and a failing `check`: the last two start no `pi`, set `doing` with the stated note, and leave no merge in progress
- [ ] Tests cover the pass path: `main` is fast-forwarded and the worktree and branch are removed
- [ ] Tests cover `main` having moved and a dirty main checkout: nothing is merged or removed, the exit is non-zero, and a later `chitty run` completes the merge once the cause is fixed
- [ ] Tests cover `check` unset as a loud error, and a third failure in a row ending `blocked` with owner `human`
- [ ] A Node test shows the review prompt no longer mentions merging or removing
- [ ] `PLAN.md`, `README.md`, `src/chitty/guide.md` and the `chitty.toml` template are updated; `chitty init` handles existing repositories; `__version__` is bumped

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T16:30:15Z lively-panda: changed title, dependencies, description, acceptance criteria
