---
title: Merge `main` into the ticket branch before every work session
status: planning
labels:
  - bug
depends_on:
  - TASK-371
created: 2026-11-18
---

## Description

A work session today runs on whatever the ticket branch last had: `_run_ticket` in `src/chitty/run.py` never merges `main` in work mode, so workers build on code behind `main`, and `setup` and `check` test code that is not what would land. Review (`_prepare_review`) and landing (`_land`) already merge `main`.

Principle (decided 2026-11-18): a ticket branch takes `main` whenever the runner touches it. Merging is mechanical and done by the runner; only resolving a code conflict is left to an agent.

Decisions:

- In work mode, `_run_ticket` merges local `main_branch` into the ticket branch right after `_worktree` and before `setup`, so `setup`, `check` and the agent see the merged code. Always merge: a branch `_worktree` has just created from `main` is already up to date, and the merge is a no-op. Applies to `todo`, `doing` and `error` tickets.
- Use `git.merge_main(root, main_branch, ticket_directories)` with the configured active and archive directories, as `TASK-359` defines it. Ticket-file-only conflicts are resolved and committed there.
- A worktree with uncommitted files (`git.uncommitted_paths`) is not merged; the run continues as today. A merge in progress is already refused by `_worktree`.
- `merge_main` aborts on any other conflict and returns the conflicting paths. Then the runner calls `_sync_ticket(worktree, task_id, main_branch)` (`TASK-371`), appends the note `Merge of main conflicted before this session in <files>: run git merge <main_branch> and resolve the conflicts.` in the worktree, and starts the agent; for an `error` ticket that is the repair agent. The merge itself changes no status; a `todo` ticket is still claimed to `doing` before the agent starts, as today.
- A merge that fails without conflicts (`merge_main` raises `ChittyError`) stops the run with that error, exit 1, leaving the ticket and branch unchanged.
- Ctrl-C during the merge aborts it, exit 130, as in `_prepare_review`.
- Update the work-mode bullet under "Before a review" in `docs/plan/next-action-and-runner.md`, and add the principle above to that file in those words.

Out of scope: auto-resolving code conflicts, and review and landing merges.

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_work_merges_main.py`, in the style of `tests/test_review_merge.py`, using `GIT_COMMITTER_DATE` where commit order matters, as `tests/test_store.py` does. No property: the behaviour is real `git merge` and runner processes over the small fixed set of cases in the criteria; the pure decisions (conflict classification, side choice) are `TASK-359`'s. Each test fails before the change.

## Acceptance Criteria

- [ ] A work run on a `doing` ticket whose branch exists, with a new non-conflicting commit on `main`, starts its fake agent in a worktree that contains that commit, and a fake `check` command records that it ran with that commit present
- [ ] A work run whose merge conflicts only in the ticket file (`main`'s copy newer) commits the merge with `main`'s copy, writes no conflict note, and starts the agent
- [ ] A work run on an `error` ticket whose merge conflicts in a code file leaves no merge in progress, syncs the ticket file to `main`'s copy byte for byte, appends the conflict note naming the file, and starts the repair agent
- [ ] A worktree with uncommitted files is not merged; and a second work run with no new commit on `main` adds no merge commit to the branch
- [ ] `docs/plan/next-action-and-runner.md` states the principle from the Description and the work-mode merge, and `make check` passes

## History

- 2026-11-18T09:13:39Z witty-ginger-falcon → planning
- 2026-11-18T09:22:43Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:25:16Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:25:17Z witty-ginger-falcon: changed dependencies, description, acceptance criteria
- 2026-11-18T09:25:21Z witty-ginger-falcon planning → todo
- 2026-11-18T09:28:17Z witty-ginger-falcon: changed description
- 2026-11-18T09:32:30Z witty-ginger-falcon todo → planning
- 2026-11-18T09:51:40Z witty-ginger-falcon: changed dependencies
