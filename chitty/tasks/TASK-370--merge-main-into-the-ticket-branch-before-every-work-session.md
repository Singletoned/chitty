---
title: Merge `main` into the ticket branch before every work session
status: planning
labels:
  - bug
depends_on:
  - TASK-359
created: 2026-11-18
---

## Description

Seen 2026-11-17 on `TASK-343`. An error repair committed `error → todo` to the ticket on `main` after the branch `task-343` last committed it. The next `chitty run` ran `check` in the worktree, then the claim (`work_repo.edit(action.id, claim_edit())` in `_run_ticket`, `src/chitty/run.py`) failed with `TASK-343's latest committed version is on branch main; run Chitty in worktree <main checkout>` and stopped the loop. Work mode never merges `main`, so the branch keeps its stale ticket copy, and workers build on code that is behind `main`.

Principle (decided 2026-11-18): a ticket branch takes `main` whenever the runner touches it. Merging is mechanical and done by the runner. Only resolving a code conflict is left to an agent.

Decisions:

- In work mode, `_run_ticket` merges local `main_branch` into an existing ticket branch right after `_worktree` and before `setup`, using `git.merge_main` (`rerere.enabled=false`), so `setup`, `check` and the agent all see the merged code. A branch that `_worktree` has just created from `main` needs no merge. This applies to `todo`, `doing` and `error` tickets.
- A worktree with uncommitted files (`git.uncommitted_paths`) is not merged; the run continues as today. A merge in progress is already refused by `_worktree`.
- Conflicts only in Chitty ticket files are resolved as `TASK-359` decides, and the merge is committed.
- Any other conflict: `git merge --abort`. If the newest committed version of the ticket is then on another branch, the runner writes that content into the worktree ticket file and commits it on the branch (`chitty: sync <ID> from <branch>`), with the same rule `TASK-359` uses. Then append the note `Merge of main conflicted before this session in <files>: run git merge <main_branch> and resolve the conflicts.` and start the work agent. For an `error` ticket, that is the repair agent. The ticket status is unchanged.
- Ctrl-C during the merge aborts it, exit 130, as in `_prepare_review`.
- Update the work-mode bullet under "Before a review" in `docs/plan/next-action-and-runner.md`, and add the principle above to that file.

Out of scope: review and landing merges (already merge `main`), and auto-resolving code conflicts.

Tests: real-Git, fake-agent tests in a new `tests/test_run_work_merges_main.py`, in the style of `tests/test_review_merge.py`. Properties do not fit: the behaviour is in real `git merge` and runner processes, with a small fixed set of cases, each listed in the criteria. Each test must fail before the change.

## Acceptance Criteria

- [ ] A work run on an existing branch, with a new commit on `main` that does not conflict, starts its fake agent in a worktree that contains that commit and whose `check` ran on the merged code
- [ ] The `TASK-343` case: `main` commits a ticket edit after the branch last committed it, and a work run claims the ticket and starts the agent without the `latest committed version` error
- [ ] A code conflict with `main` aborts the merge, leaves no merge in progress, syncs a newer ticket file from `main` into the branch, appends the conflict note naming the files, and starts the agent with the status unchanged
- [ ] A worktree with uncommitted files is not merged and the run proceeds as before
- [ ] `docs/plan/next-action-and-runner.md` states the principle and the work-mode merge, and `make check` passes

## History

- 2026-11-18T09:13:39Z witty-ginger-falcon → planning
- 2026-11-18T09:22:43Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:25:16Z witty-ginger-falcon cold-read → planning
