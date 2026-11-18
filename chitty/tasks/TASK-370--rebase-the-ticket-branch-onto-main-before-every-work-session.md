---
title: Rebase the ticket branch onto `main` before every work session
status: todo
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-372
  - TASK-373
  - TASK-374
  - TASK-359
created: 2026-11-18
---

## Description

A work session today runs on whatever the ticket branch last had: `_run_ticket` in `src/chitty/run.py` never brings in `main` in work mode. Workers build on code behind `main`, `setup` and `check` test code that is not what would land, and a ticket edit made on `main` (for example by an error repair) leaves the branch's copy stale (`TASK-343`, 2026-11-17).

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

Decisions:

- In work mode, after the claim on `main` (`TASK-372`) and `_worktree`, and before `setup`, call `git.rebase_onto(worktree, main_branch, ticket_directories)` (`TASK-374`) for every ticket status. Ticket-file-only stops are resolved inside it.
- Uncommitted files are stashed and restored by `--autostash`. Uncommitted files at the start of a run are an error state, so the amount stashed should be small. If restoring the stash conflicts, Git keeps it in the stash list: record a ticket error (`_record_ticket_error`, phase `rebase`) whose note says the work is in the stash, and start no agent.
- On a code conflict, leave the rebase stopped, skip `setup` and `check`, and start the agent: the work agent, or the repair agent for an `error` ticket. Its prompt starts with the rebase instructions (`TASK-373`). Write nothing to the ticket while the rebase is stopped.
- A rebase still in progress at the start of a later run is refused by `_worktree`, as today, for a human.
- Ctrl-C during the rebase aborts it, exit 130, handled in `_run_ticket` as `_prepare_review` does. No test: it needs a signal mid-rebase.
- A `doing` ticket with no branch gets one from `main` through `_worktree`, so its rebase is a no-op.
- Update the work-mode bullet under "Before a review" in `docs/plan/next-action-and-runner.md`.

Out of scope: review and landing (`TASK-374`, `TASK-375`).

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_work_rebases.py`, in the style of `tests/test_review_merge.py`, using `GIT_COMMITTER_DATE` where order matters, as `tests/test_store.py` does. The fake agent records what it saw when it started (`git status`, files, its prompt) in a marker file. No property: real Git and runner processes over the fixed cases in the criteria; the pure decision is `merge_ticket`'s (`TASK-359`). Each test fails before the change.

## Acceptance Criteria

- [ ] A work run on a `doing` ticket whose branch exists, with a new non-conflicting commit on `main`: afterwards `git merge-base --is-ancestor main HEAD` succeeds and `git rev-list main..HEAD` lists only the branch's own commits, and a fake `check` command writes `git log --format=%H` to a marker file that contains `main`'s new commit before the agent starts
- [ ] The `TASK-343` case on a `todo` ticket whose branch exists: `main` and the branch each appended a different note to the ticket; the work run completes the rebase, the ticket has both notes and is `doing`, and the agent starts; the test fails before the change
- [ ] A work run on an `error` ticket whose rebase stops on a code file starts the repair agent with `git.rebase_in_progress(worktree)` true and the prompt starting with the rebase instructions (both recorded by the fake agent), and a fake `setup` and `check` record that they did not run
- [ ] An uncommitted change to a tracked file and an untracked file, neither touched by `main`, are back in the worktree, uncommitted, when the agent starts
- [ ] When restoring the stash conflicts (`main` changed the same lines as an uncommitted edit), the ticket moves to `error` with a `Runner error (rebase)` note saying the work is in the stash, the stash entry exists, and no agent starts; `make check` passes

## History

- 2026-11-18T09:13:39Z witty-ginger-falcon → planning
- 2026-11-18T09:22:43Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:25:16Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:25:17Z witty-ginger-falcon: changed dependencies, description, acceptance criteria
- 2026-11-18T09:25:21Z witty-ginger-falcon planning → todo
- 2026-11-18T09:28:17Z witty-ginger-falcon: changed description
- 2026-11-18T09:32:30Z witty-ginger-falcon todo → planning
- 2026-11-18T09:51:40Z witty-ginger-falcon: changed dependencies
- 2026-11-18T09:51:42Z witty-ginger-falcon: changed dependencies
- 2026-11-18T09:51:44Z witty-ginger-falcon: changed title, labels, priority, dependencies, description, acceptance criteria
- 2026-11-18T09:52:37Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:54:24Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:54:26Z witty-ginger-falcon: changed dependencies, description, acceptance criteria
- 2026-11-18T09:54:27Z witty-ginger-falcon planning → todo
