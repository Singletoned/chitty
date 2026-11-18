---
title: Remove local ticket branches that `main` already contains
status: todo
depends_on:
  - TASK-396
parent: TASK-376
created: 2026-11-18
---

## Description

Under the one-authoritative-copy model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket branch whose tip `main` contains is merged or stale, and reads ignore it (`TASK-377` rule 2). The owner decided on 2026-11-18 that such branches should go: if a branch equals `main`, or is behind it (which a rebase would turn into equal), delete it. Reads never do this; the runner does, as a clean-up step. (None of the nine local `task-*` branches was merged on 2026-11-18, but landed branches left behind by a failed clean-up and branches made but never worked will be.)

Starts after `TASK-396` (`git.is_ancestor`) lands.

Decisions:

- At the start of every `chitty run` (before `_land_pending` and selection), under `locks.landing_lock` (so it cannot race a landing between its fast-forward and its worktree removal), after `git worktree prune` (so a worktree whose directory was deleted by hand is forgotten rather than crashing the run), the runner removes each local ticket branch (a local branch named a configured context prefix plus `-<suffix>`, lower-cased: `task-5`, `human-12`) whose tip `main` contains, using `git.is_ancestor(root, <branch tip>, <main tip>)`: first its linked worktree, if any, then the branch (`git.remove_worktree`, `git.delete_branch`). It prints `removed merged branch <b>` to stderr for each.
- It leaves a branch alone, printing `kept merged branch <b>: <reason>`, when its ticket's run lock is held (`locks.is_locked`: a run in another session may have just made the branch from `main`), when its worktree has uncommitted or untracked files, or a merge or rebase in progress, or is the main checkout, or when removing the worktree or branch raises `ChittyError` (the reason is the error; the run carries on). Ignored files (such as `.venv/`) do not keep a branch: ticket worktrees are the runner's disposable workspaces.
- Remote-tracking branches are never deleted: they are not this machine's.
- A branch with commits `main` lacks is left alone, whatever its ticket says.
- Update `docs/plan/next-action-and-runner.md` with the clean-up step.

Tests: real-Git runner tests in a new `tests/test_run_removes_merged_branches.py`, in the style of `tests/test_landing.py` (configured `setup` and `check`, fake agent), with `git init -b main`. No property: a fixed set of branch states, each in the criteria.

## Acceptance Criteria

- [ ] `chitty run` removes a local `task-<n>` equal to `main` and one behind `main`, with their clean worktrees, and prints `removed merged branch` for each; this fails before the change
- [ ] It keeps, with a `kept merged branch` line, a merged branch whose run lock is held, one whose worktree has an uncommitted file, one with a rebase in progress, and one with a merge in progress; it never removes a branch ahead of `main`, a non-ticket branch such as `feature`, or a remote-tracking `origin/task-<n>`; a worktree whose directory was deleted by hand does not stop the run
- [ ] `docs/plan/next-action-and-runner.md` says the clean-up runs at the start of `chitty run`, before pending landings, under the landing lock, lists the reasons a merged branch is kept, and gives the `removed merged branch` and `kept merged branch` lines; `make check` passes

## History

- 2026-11-18T18:00:02Z lively-quartz-crane → backlog
- 2026-11-18T18:00:04Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:00:04Z lively-quartz-crane backlog → cold-read
- 2026-11-18T18:02:13Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:02:13Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:02:15Z lively-quartz-crane planning → todo
