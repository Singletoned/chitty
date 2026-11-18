---
title: Rebase the ticket branch onto `main` before every work session
status: cold-read
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-373
  - TASK-374
  - TASK-384
  - TASK-382
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model a ticket file changes only on its branch, so ticket files rebase like any other file; there is no ticket merge (`TASK-359` is archived). Any conflict goes to an agent.

A work session today runs on whatever the ticket branch last had: `_run_ticket` in `src/chitty/run.py` never brings in `main` in work mode, so workers build on code behind `main`, and `setup` and `check` test code that is not what would land.

Starts after `TASK-374` (`git.rebase_onto`), `TASK-373` (rebase instructions in the work and repair guides), `TASK-382` (`branch_repo`) and `TASK-384` (claim on the branch) land.

Decisions:

- In work mode, after `_worktree` and the claim (`TASK-384`) and before `setup`, rebase the worktree onto `main` for every ticket status.
- Uncommitted work is cheap to redo (decided with the owner 2026-11-18), so stash it explicitly rather than with `--autostash`, which a cold read showed can report success with conflict markers left behind, hide edits during a stopped rebase, and break the next run:
  1. If the worktree has uncommitted or untracked (not ignored) files, `git stash push --include-untracked -m "chitty <ID> before rebase"` and keep the stash commit's ID (`git rev-parse stash@{0}` straight after): the stash list is shared by every worktree, so always refer to the entry by that ID and, to drop it, find its current `stash@{n}` by ID first.
  2. Rebase with `git.rebase_onto` (`TASK-374`); `rebase_onto` itself never uses `--autostash` here (add a parameter, or make it never autostash, and say which in the commit).
  3. If the rebase completed: `git stash apply <ID>`. On success, drop the entry. On a conflict, reset the worktree to `HEAD` (`git reset --hard` and `git clean -fd`, which keeps ignored files), keep the entry, and add a note on the ticket through `branch_repo`: `Uncommitted changes from before the rebase did not apply cleanly; they are in stash <ID>.` Then carry on.
  4. If the rebase stopped on a conflict (any file): leave it stopped and the stash entry in place, skip `setup` and `check`, and start the agent (the work agent, or the repair agent for an `error` ticket). Write nothing to the ticket while the rebase is stopped. When a stash was made, the agent's prompt also says `Uncommitted changes from before the rebase are in stash <ID>; re-apply them after the rebase if they are still useful.`
- Render the agent command (`_agent_command`) after `_worktree` and the rebase, passing the worktree to `guide()` as `TASK-373` defines, so the prompt reflects the stopped rebase. Today it is rendered before `_worktree`.
- A `rebase_onto` error that is not a conflict is recorded as a ticket error on the branch (`_record_ticket_error(branch_repo, ...)`, phase `rebase`); no agent starts.
- A rebase still in progress at the start of a later run is refused by `_worktree`, as today, for a human.
- Ctrl-C during the rebase aborts it and raises `RunInterrupted("rebase")` (exit 130); the stash entry stays. No test: it needs a signal mid-rebase.
- Update the work-mode bullet under `## Before a review` in `docs/plan/next-action-and-runner.md`.

Tests: real-Git, fake-agent runner tests in a new `tests/test_run_work_rebases.py`, in the style of `tests/test_review_merge.py`, with `git init -b main`. The fake agent records what it saw when it started (`git status`, `git.rebase_in_progress`, `git stash list`, its prompt) in a marker file. No property: real Git and runner processes over the fixed cases in the criteria.

## Acceptance Criteria

- [ ] A work run on a `doing` ticket whose branch exists, with a new non-conflicting commit on `main`: afterwards `main` is an ancestor of the branch and `git rev-list main..task-<n>` lists only the branch's own commits, and a fake `check` command records `main`'s new commit in `git log` before the agent starts; this fails before the change
- [ ] A work run on an `error` ticket whose rebase stops on a code conflict starts the repair agent with a rebase in progress and a prompt containing the rebase instructions after its first line (both recorded by the fake agent), and a fake `setup` and `check` record that they did not run
- [ ] After `main` gains a commit touching another file, an unstaged edit to a tracked file, a staged edit and an untracked file are all present with the same content when the agent starts, the branch has been rebased, and `git stash list` has no entry left by the run; this fails before the change
- [ ] When applying the stash conflicts (`main` changed the same lines as an uncommitted edit), the worktree matches `HEAD` when the agent starts, the stash entry exists and is named by ID in a note on the branch's ticket, and the agent starts; when the rebase stops on a conflict with a stash made, the prompt names the stash ID
- [ ] A `rebase_onto` failure that is not a conflict records `Runner error (rebase)` on the branch and starts no agent; `make check` passes

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
- 2026-11-18T17:58:13Z lively-quartz-crane: changed dependencies
- 2026-11-18T18:00:07Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:16:56Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T18:16:56Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:16:58Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T18:17:00Z lively-quartz-crane planning → cold-read
