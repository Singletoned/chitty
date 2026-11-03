---
title: Merge and check around reviews in `chitty run`, fast-forwarding `main` after a pass
status: todo
priority: high
depends_on:
  - TASK-126
created: 2026-11-03
---

## Description

Merging is mechanical and has gone wrong. The global `chitty` is an editable install of the main checkout, so a conflicted merge there leaves conflict markers in `src/chitty/*.py` and breaks `chitty` in every repository until it is resolved (`TASK-118`). `TASK-104` also spent a full review to learn that its branch would not merge. Have `chitty run` do it, around the review.

All new logic goes in `src/chitty/run.py`, with Git helpers in `src/chitty/git.py`. Automatic status moves go through `Repo.edit`, so `_escalate_repeated_failure` counts them and the third becomes `blocked` with owner `human`. They use the run's own actor from `TASK-126`, which never worked on the ticket, so the independence check allows them.

### Before starting a review session

In this order, in the ticket's worktree, with `check` unset as a loud error before anything is touched:

1. If the worktree has uncommitted changes, including untracked files, move the ticket to `doing` with `Review failed (work): ...` listing them. An unfinished merge left by a crash is a loud error for the human, with no status change.
2. Merge `main` into the branch. On a conflict, abort the merge and move the ticket to `doing` with `Review failed (integration): ...` naming the conflicting files.
3. Run `setup` from `TASK-126`, after the merge because the merge can change dependencies.
4. Run the new `check` command from `chitty.toml`, parsed without a shell like `autoformat`, and with no default for the same reason as `setup`. On failure, move the ticket to `doing` with `Review failed (work): ...` and the last 20 lines of output. Set `check = "make check"` in this repository, and add `npm test` to `make check`, which does not currently run the Node tests.
5. After any of those failures, do not start Pi. No review is spent on work that cannot pass, and `chitty run` exits 0 because the status changed.

The reviewer therefore sees the merged tree. Ctrl-C during the merge or check aborts any merge and exits 130.

### Landing a `done` ticket

A pending ticket is a non-archived `done` ticket with a local branch named `<id in lower case>`. Find it by branch name, not `StoredTask.branch`, which is `None` once the file matches `main`. Legacy branches with other names are ignored, and remote refs are never touched.

After a session that moves its ticket to `done`, and also at the start of every `chitty run`, for each pending ticket in ID order, stopping at the first failure:

1. Refuse, with a message and a non-zero exit, if the main checkout is not on branch `main` or has changes to tracked files. Untracked files are allowed: `git merge` already refuses a real collision, and this repository's main checkout often has some.
2. If `main` is not an ancestor of the branch, merge `main` into the branch in its worktree, then run `setup` and `check`. Ticket commits land on `main` often, so this will be common. A clean merge with a passing `check` lands without another review, because both sides were already accepted; decided by the author, cheap to change. On a conflict or failed check, abort any merge, leave everything in place, and exit non-zero naming the problem, for the human to resolve in the worktree.
3. Run `git merge --ff-only <branch>` in the main checkout. Never resolve anything there.
4. Remove the worktree with `git worktree remove` and the branch with `git branch -d`, never forced. A failure exits non-zero, and a later run repeats this step, because every step above is a no-op once done.

A successful landing at the start of a run carries on to selection as normal. A failure stops the run before selection. This exit overrides the `TASK-124` rule that a changed status exits 0, so update its tests where needed.

### Prompts and docs

The Pi review prompt stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to merge `main` into the branch in the worktree first, then only fast-forward `main`.

Out of scope: pushing, repositories whose main branch is not `main`, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests with a fake `pi` and a real Git repository cover a clean merge, a conflict and a failing `check`: the last two start no `pi`, set `doing` with the stated note, and leave no merge in progress
- [ ] Tests cover the pass path: `main` is fast-forwarded and the worktree and branch are removed
- [ ] Tests cover `main` having moved and a dirty main checkout: nothing is merged or removed, the exit is non-zero, and a later `chitty run` completes the merge once the cause is fixed
- [ ] Tests cover `check` unset as a loud error, and a third failure in a row ending `blocked` with owner `human`
- [ ] A Node test shows the review prompt no longer mentions merging or removing
- [ ] `PLAN.md`, `README.md`, `src/chitty/guide.md` and the `chitty.toml` template are updated; `chitty init` handles existing repositories; `__version__` is bumped
- [ ] Tests cover the review preparation order: the tree the fake `pi` receives contains the merge from `main`, `setup` ran after the merge, and uncommitted files move the ticket to `doing` without starting `pi`
- [ ] Tests pin the failure notes: a conflict names the files, a failed `check` carries the last 20 lines, and a mix of automatic and reviewer failures reaches the limit together
- [ ] Tests cover landing when `main` has moved: a clean merge with a passing `check` lands, while a conflict or failing `check` leaves everything in place and exits non-zero, and a later run lands it once resolved
- [ ] Tests cover the main checkout on another branch and with untracked files: the first refuses, the second lands
- [ ] Tests cover two pending tickets landing in ID order at the start of a run, a stop at the first failure, a leftover unfinished merge, and a retry after a failed worktree removal
- [ ] A test uses a quoted argument in `check`, showing it is parsed without a shell, and `make check` runs the Node tests

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. The biggest find: autocommitted ticket commits move `main` often, so `--ff-only` alone would refuse most landings; it now merges and rechecks. Also adopted: untracked files allowed in the main checkout (the old rule would have refused every merge here because of `chats/`), the main checkout must be on `main`, pending tickets found by branch name, `setup` after the merge, and `make check` running Node tests. Authors choice for the reviewer: a clean re-merge lands without another review.

As in `TASK-126`, read `check` from the main checkout config, so older branches have it.

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T16:30:15Z lively-panda: changed title, dependencies, description, acceptance criteria
- 2026-11-03T16:48:16Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T16:49:00Z lively-panda: changed notes
