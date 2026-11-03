---
title: Rebase and check around reviews in `chitty run`, fast-forwarding `main` after a pass
status: todo
priority: high
depends_on:
  - TASK-126
created: 2026-11-03
---

## Description

Landing work is mechanical and has gone wrong. The global `chitty` is an editable install of the main checkout, so a conflicted merge there leaves conflict markers in `src/chitty/*.py` and breaks `chitty` in every repository until it is resolved (`TASK-118`). `TASK-104` also spent a full review to learn that its branch would not merge. Have `chitty run` do it, around the review, using rebase so `main` stays linear.

All new logic goes in `src/chitty/run.py`, with Git helpers in `src/chitty/git.py`. Automatic status moves go through `Repo.edit`, so `_escalate_repeated_failure` counts them and the third becomes `blocked` with owner `human`. They use the run's own actor from `TASK-126`, which never worked on the ticket, so the independence check allows them. `check` is read from the main checkout's config, as `setup` is.

Decided with the human, 2026-11-03: rebase at the start of review. Main changing significantly during a review is unlikely, so no second review after a clean re-rebase. Untracked files are unwanted in the main checkout, so they block landing.

### Before starting a review session

In this order, in the ticket's worktree. `check` unset is a loud error in the `TASK-126` preflight, in every mode, so a repository finds out before work starts, not at review:

1. If the worktree has uncommitted changes, including untracked files, move the ticket to `doing` with `Review failed (work): ...` listing them. A rebase left unfinished by a crash is a loud error for the human, with no status change.
2. Rebase the branch onto `main`. On a conflict, run `git rebase --abort` and move the ticket to `doing` with `Review failed (integration): ...` naming the conflicting files. The worker resolves it in a fresh session.
3. Run `setup` from `TASK-126`, after the rebase because it can change dependencies.
4. Run the new `check` command, parsed without a shell like `autoformat`, and with no default for the same reason as `setup`. On failure, move the ticket to `doing` with `Review failed (work): ...` and the last 20 lines of output. Set `check = "make check"` in this repository, and add `npm test` to `make check`, which does not currently run the Node tests.
5. After any of those failures, do not start Pi. No review is spent on work that cannot pass, and `chitty run` exits 0 because the status changed.

The reviewer therefore sees exactly what will land. Ctrl-C during the rebase or check aborts any rebase and exits 130.

### Landing a `done` ticket

A pending ticket is a non-archived `done` ticket with a local branch named `<id in lower case>`. Find it by branch name, not `StoredTask.branch`, which is `None` once the file matches `main`. Legacy branches with other names are ignored, and remote refs are never touched.

After a session that moves its ticket to `done`, and also at the start of every `chitty run`, for each pending ticket in ID order, stopping at the first failure:

1. Refuse, with a message and a non-zero exit, if the main checkout is not on branch `main` or is not clean, using the existing `git.require_clean`, which includes untracked files. Ignored files are allowed. Also refuse if the ticket's worktree has uncommitted changes, including untracked files; otherwise they would only surface when removal fails, after landing. If the branch has no worktree, add one as in `TASK-126`.
2. If `main` is not an ancestor of the branch, rebase the branch onto `main` in its worktree, then run `setup` and `check`. Ticket commits land on `main` often, so this will be common. A clean rebase with a passing `check` lands without another review. On a conflict or failed check, abort any rebase, leave everything in place, and exit non-zero naming the problem, for the human to resolve in the worktree.
3. Run `git merge --ff-only <branch>` in the main checkout. Never resolve anything there.
4. Remove the worktree with `git worktree remove` and the branch with `git branch -d`, never forced. A failure exits non-zero, and a later run repeats this step, because every step above is a no-op once done.

A successful landing at the start of a run carries on to selection as normal. A failure stops the run before selection. This exit overrides the `TASK-124` rule that a changed status exits 0, so update its tests where needed.

### Prompts and docs

The Pi review prompt stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to rebase the branch onto `main` in the worktree first, then only fast-forward `main`.

Out of scope: pushing, repositories whose main branch is not `main`, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests with a fake `pi` and a real Git repository cover review preparation: the tree `pi` receives is rebased on `main`, the branch history is linear, and `setup` ran after the rebase
- [ ] Tests cover a rebase conflict, a failing `check` and uncommitted files: none starts `pi`, each moves the ticket to `doing` with the stated note, and no rebase is left in progress. A conflict note names the files and a failed `check` note carries the last 20 lines
- [ ] Tests show a mix of automatic and reviewer failures reaching the limit together, ending `blocked` with owner `human`, and `check` unset as a loud error before anything changes
- [ ] Tests cover the pass path: `main` is fast-forwarded with a linear history, and the worktree and branch are removed
- [ ] Tests cover landing when `main` has moved: a clean rebase with a passing `check` lands, while a conflict or failing `check` leaves everything in place and exits non-zero, and a later run lands it once resolved
- [ ] Tests cover the main checkout on another branch, with a tracked change and with an untracked file: each refuses and changes nothing, while an ignored file lands
- [ ] Tests cover two pending tickets landing in ID order at the start of a run, a stop at the first failure, a leftover unfinished rebase, and a retry after a failed worktree removal
- [ ] A test uses a quoted argument in `check`, showing it is parsed without a shell, and `make check` runs the Node tests
- [ ] A Node test shows the review prompt no longer mentions merging or removing
- [ ] `PLAN.md`, `README.md`, `src/chitty/guide.md` and the `chitty.toml` template are updated; `chitty init` handles existing repositories; `__version__` is bumped
- [ ] Tests show that after landing the ticket on `main` is `done`, and that uncommitted files in the worktree refuse landing with nothing changed
- [ ] This repository sets `check = "make check"`, and a test shows `chitty init` adds `check` to an existing repository only as a commented example

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. The biggest find: autocommitted ticket commits move `main` often, so `--ff-only` alone would refuse most landings; it now merges and rechecks. Also adopted: untracked files allowed in the main checkout (the old rule would have refused every merge here because of `chats/`), the main checkout must be on `main`, pending tickets found by branch name, `setup` after the merge, and `make check` running Node tests. Authors choice for the reviewer: a clean re-merge lands without another review.

As in `TASK-126`, read `check` from the main checkout config, so older branches have it.

Changed with the human after the cold read: rebase replaces merging `main` into the branch, so earlier mentions of merging are superseded, and untracked files now block landing.

Every finding from the cold read now has an outcome. Fixed in the ticket on the second pass: uncommitted worktree files at landing, which I had missed and which would have failed only after landing; a branch with no worktree; `check` unset failing in every mode, not at the first review; `done` reaching `main`; this repository's `check`; and the `init` migration. Rejected: a `check` timeout, because a hang is visible and none has happened. The order of the printed change line, because nothing depends on it. A conflict in the ticket file after an aborted rebase, because `TASK-105` refuses `main` edits while a ticket is on a branch. A registered worktree whose directory has gone, because Git fails loudly. An abandoned branch named `task-N` stopping runs, because that is loud and needs a person. Overlap with `TASK-126` in `guide.md`, because `TASK-126` leaves it alone. Open for the human: `task-118` is a `done` ticket with an unlanded branch, so the first run after this lands would rebase and land it.

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T16:30:15Z lively-panda: changed title, dependencies, description, acceptance criteria
- 2026-11-03T16:48:16Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T16:49:00Z lively-panda: changed notes
- 2026-11-03T17:26:53Z lively-panda: changed title, description, acceptance criteria, notes
- 2026-11-03T20:00:16Z lively-panda: changed description, acceptance criteria, notes
