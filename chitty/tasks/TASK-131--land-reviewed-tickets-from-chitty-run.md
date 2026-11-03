---
title: Land reviewed tickets from `chitty run`
status: todo
priority: high
depends_on:
  - TASK-120
parent: TASK-106
created: 2026-11-03
---

## Description

Second half of `TASK-120`, which rebases and checks before a review. After a pass, have `chitty run` land the work, so reviewers no longer merge in the main checkout, where a conflict breaks `chitty` for every repository (`TASK-118`). Logic goes in `src/chitty/run.py`, with Git helpers in `src/chitty/git.py`.

### Landing a `done` ticket

A pending ticket is a non-archived `done` ticket with a local branch named `<id in lower case>`. Find it by branch name, not `StoredTask.branch`, which is `None` once the file matches `main`. Legacy branches with other names are ignored, and remote refs are never touched.

After a session that moves its ticket to `done`, and also at the start of every `chitty run`, for each pending ticket in ID order, stopping at the first failure:

1. Refuse, with a message and a non-zero exit, if the main checkout is not on branch `main` or is not clean, using the existing `git.require_clean`, which includes untracked files. Ignored files are allowed. Also refuse if the ticket's worktree has uncommitted changes, including untracked files; otherwise they would only surface when removal fails, after landing. If the branch has no worktree, add one as in `TASK-126`.
2. If `main` is not an ancestor of the branch, rebase the branch onto `main` in its worktree, then run `setup` and `check`. Ticket commits land on `main` often, so this will be common. A clean rebase with a passing `check` lands without another review. On a conflict or failed check, abort any rebase, leave everything in place, and exit non-zero naming the problem, for the human to resolve in the worktree.
3. Run `git merge --ff-only <branch>` in the main checkout. Never resolve anything there. Then run `chitty init` there as a new process, because the running process still holds the old code. That is how a bumped version and a new Pi extension reach this machine, since `TASK-129` stops worktrees installing them.
4. Remove the worktree with `git worktree remove` and the branch with `git branch -d`, never forced. A failure exits non-zero, and a later run repeats this step, because every step above is a no-op once done.

A successful landing at the start of a run carries on to selection as normal. A failure stops the run before selection. This exit overrides the `TASK-124` rule that a changed status exits 0, so update its tests where needed.

### Prompts and docs

The Pi review prompt stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to rebase the branch onto `main` in the worktree first, then only fast-forward `main`.

Out of scope: pushing, repositories whose main branch is not `main`, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests cover the pass path: `main` is fast-forwarded with a linear history, and the worktree and branch are removed
- [ ] Tests cover landing when `main` has moved: a clean rebase with a passing `check` lands, while a conflict or failing `check` leaves everything in place and exits non-zero, and a later run lands it once resolved
- [ ] Tests cover the main checkout on another branch, with a tracked change and with an untracked file: each refuses and changes nothing, while an ignored file lands
- [ ] Tests cover two pending tickets landing in ID order at the start of a run, a stop at the first failure, a leftover unfinished rebase, and a retry after a failed worktree removal
- [ ] A Node test shows the review prompt no longer mentions merging or removing
- [ ] Tests show that after landing the ticket on `main` is `done`, and that uncommitted files in the worktree refuse landing with nothing changed
- [ ] A test shows that landing a version bump upgrades setup in the main checkout and installs the extension into a temporary `PI_CODING_AGENT_DIR`
- [ ] `PLAN.md`, `README.md` and `src/chitty/guide.md` describe landing; `__version__` is bumped above `main`'s

## History

- 2026-11-03T20:46:17Z lively-panda → todo
