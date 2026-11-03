---
title: Rebase and check before reviews in `chitty run`
status: todo
priority: high
depends_on:
  - TASK-126
  - TASK-129
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

After a pass, `TASK-131` lands the ticket. Until then, reviewers merge as the guide says.

Out of scope: landing, pushing, repositories whose main branch is not `main`, the spec-test gates for the pilot's tests stage, and non-Pi harnesses.

## Acceptance Criteria

- [ ] Tests with a fake `pi` and a real Git repository cover review preparation: the tree `pi` receives is rebased on `main`, the branch history is linear, and `setup` ran after the rebase
- [ ] Tests cover a rebase conflict, a failing `check` and uncommitted files: none starts `pi`, each moves the ticket to `doing` with the stated note, and no rebase is left in progress. A conflict note names the files and a failed `check` note carries the last 20 lines
- [ ] Tests show a mix of automatic and reviewer failures reaching the limit together, ending `blocked` with owner `human`, and `check` unset as a loud error before anything changes
- [ ] A test uses a quoted argument in `check`, showing it is parsed without a shell, and `make check` runs the Node tests
- [ ] This repository sets `check = "make check"`, and a test shows `chitty init` adds `check` to an existing repository only as a commented example
- [ ] `PLAN.md`, `README.md` and the `chitty.toml` template document `check`; `chitty init` handles existing repositories; `__version__` is bumped above `main`'s

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-03. The biggest find: autocommitted ticket commits move `main` often, so `--ff-only` alone would refuse most landings; it now merges and rechecks. Also adopted: untracked files allowed in the main checkout (the old rule would have refused every merge here because of `chats/`), the main checkout must be on `main`, pending tickets found by branch name, `setup` after the merge, and `make check` running Node tests. Authors choice for the reviewer: a clean re-merge lands without another review.

As in `TASK-126`, read `check` from the main checkout config, so older branches have it.

Changed with the human after the cold read: rebase replaces merging `main` into the branch, so earlier mentions of merging are superseded, and untracked files now block landing.

Every finding from the cold read now has an outcome. Fixed in the ticket on the second pass: uncommitted worktree files at landing, which I had missed and which would have failed only after landing; a branch with no worktree; `check` unset failing in every mode, not at the first review; `done` reaching `main`; this repository's `check`; and the `init` migration. Rejected: a `check` timeout, because a hang is visible and none has happened. The order of the printed change line, because nothing depends on it. A conflict in the ticket file after an aborted rebase, because `TASK-105` refuses `main` edits while a ticket is on a branch. A registered worktree whose directory has gone, because Git fails loudly. An abandoned branch named `task-N` stopping runs, because that is loud and needs a person. Overlap with `TASK-126` in `guide.md`, because `TASK-126` leaves it alone. Open for the human: `task-118` is a `done` ticket with an unlanded branch, so the first run after this lands would rebase and land it.

Added after the `TASK-129` cold read: without this step, nothing would install a new extension after landing.

Split on 2026-11-03 at the human's prompting, because 13 criteria was too large: landing moved unchanged to `TASK-131`.

## History

- 2026-11-03T11:39:03Z eager-raven → todo
- 2026-11-03T16:30:15Z lively-panda: changed title, dependencies, description, acceptance criteria
- 2026-11-03T16:48:16Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T16:49:00Z lively-panda: changed notes
- 2026-11-03T17:26:53Z lively-panda: changed title, description, acceptance criteria, notes
- 2026-11-03T20:00:16Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-03T20:44:55Z lively-panda: changed dependencies, description, acceptance criteria, notes
- 2026-11-03T20:46:17Z lively-panda: changed title, description, acceptance criteria, notes
