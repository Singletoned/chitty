---
title: Rebase the ticket branch onto `main` before every work session
status: planning
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-372
  - TASK-373
  - TASK-374
  - TASK-384
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model a ticket file changes only on its branch, so ticket files rebase like any other file; there is no ticket merge (`TASK-359` is archived). Any conflict, ticket file or not, goes to an agent.

A work session today runs on whatever the ticket branch last had: `_run_ticket` in `src/chitty/run.py` never brings in `main` in work mode, so workers build on code behind `main`, and `setup` and `check` test code that is not what would land.

Starts after `TASK-374` (`git.rebase_onto`), `TASK-373` (rebase instructions in the work and repair guides) and `TASK-384` (claim on the branch) land.

Decisions:

- In work mode, after `_worktree` and the claim (`TASK-384`) and before `setup`, call `git.rebase_onto(worktree, main_branch)` for every ticket status.
- Uncommitted files are stashed and restored by `--autostash`. If restoring the stash conflicts, Git keeps it in the stash list: record a ticket error on the branch (`_record_ticket_error`, phase `rebase`) whose note says the work is in the stash, and start no agent.
- On a conflict (any file), leave the rebase stopped, skip `setup` and `check`, and start the agent: the work agent, or the repair agent for an `error` ticket. Its prompt starts with the rebase instructions (`TASK-373`). Write nothing to the ticket while the rebase is stopped.
- A rebase still in progress at the start of a later run is refused by `_worktree`, as today, for a human.
- Ctrl-C during the rebase aborts it and raises `RunInterrupted` (exit 130). No test: it needs a signal mid-rebase.
- A ticket whose branch is new from `main` rebases as a no-op.
- Update the work-mode bullet under `## Before a review` in `docs/plan/next-action-and-runner.md`.

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_work_rebases.py`, in the style of `tests/test_review_merge.py`, with `git init -b main`. The fake agent records what it saw when it started (`git status`, `git.rebase_in_progress`, its prompt) in a marker file. No property: real Git and runner processes over the fixed cases in the criteria.

## Acceptance Criteria

- [ ] A work run on a `doing` ticket whose branch exists, with a new non-conflicting commit on `main`: afterwards `main` is an ancestor of the branch and `git rev-list main..task-<n>` lists only the branch's own commits, and a fake `check` command records `main`'s new commit in `git log` before the agent starts; this fails before the change
- [ ] A work run on an `error` ticket whose rebase stops on a code conflict starts the repair agent with a rebase in progress and a prompt starting with the rebase instructions (both recorded by the fake agent), and a fake `setup` and `check` record that they did not run
- [ ] An uncommitted change to a tracked file and an untracked file, neither touched by `main`, are back in the worktree, uncommitted, when the agent starts
- [ ] When restoring the stash conflicts (`main` changed the same lines as an uncommitted edit), the ticket moves to `error` on the branch with a `Runner error (rebase)` note saying the work is in the stash, the stash entry exists, and no agent starts; `make check` passes

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

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
- 2026-11-18T15:47:42Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:42Z witty-ginger-falcon todo → planning
- 2026-11-18T17:57:44Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:57:46Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:57:48Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:57:51Z lively-quartz-crane: changed dependencies
