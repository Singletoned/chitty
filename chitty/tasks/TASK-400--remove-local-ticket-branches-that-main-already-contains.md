---
title: Remove local ticket branches that `main` already contains
status: doing
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
- It also keeps a merged branch whose ticket exists and is not `done`, printing `kept merged branch <b>: <ID> is <status>` (status from `Repo.lookup(<ID>)`). Only branches of `done` tickets, archived or not, and of IDs no ticket has, are removed. Decided 2026-11-20 after a worker found that removing the branch of a `review` ticket makes the runner error it (a review needs its branch), and that runner tests and real runs create a `doing` ticket's branch at `main`'s tip; such branches are harmless, because work reuses them.
- Remote-tracking branches are never deleted: they are not this machine's.
- A branch with commits `main` lacks is left alone, whatever its ticket says.
- Update `docs/plan/next-action-and-runner.md` with the clean-up step.

Tests: real-Git runner tests in a new `tests/test_run_removes_merged_branches.py`, in the style of `tests/test_landing.py` (configured `setup` and `check`, fake agent), with `git init -b main`. No property: a fixed set of branch states, each in the criteria.

Fixtures for criterion 2, each its own test: run lock held: hold `locks.run_lock(root, "TASK-<n>")` (`src/chitty/locks.py`) in the test process across the `chitty run` call; uncommitted file: write an untracked `x.txt` in the branch's worktree; rebase in progress: in the worktree, commit a change to `a.txt` that conflicts with a commit on `main`, then `git rebase main` and leave it stopped; merge in progress: the same conflict with `git merge main` stopped; deleted worktree: `shutil.rmtree` the worktree directory before `chitty run`. For the rebase and merge fixtures the branch is not merged while stopped, so assert only that the run completes and the branch still exists. Also add to `tests/test_run_repair_on_branch.py`, in the test that creates an `error` ticket's branch at `main`'s tip, an assertion that stderr contains `kept merged branch task-<n>: TASK-<n> is error` and not `removed merged branch` (comparing tip SHAs would not show it: a branch recreated from `main` has the same tip).

## Acceptance Criteria

- [ ] `chitty run` removes, for `done` tickets, a local `task-<n>` equal to `main` with a clean linked worktree (both removed) and one behind `main` with no worktree, and a merged branch for an ID no ticket has, and prints `removed merged branch` for each; this fails before the change
- [ ] It keeps, with a `kept merged branch` line, a merged branch for each non-`done` status (`todo`, `doing`, `review`, `error`, `blocked`), each printing `<ID> is <status>`, a merged branch whose run lock is held, one whose worktree has an uncommitted file, one with a rebase in progress, and one with a merge in progress; it never removes a branch ahead of `main`, a non-ticket branch such as `feature`, or a remote-tracking `origin/task-<n>`; a worktree whose directory was deleted by hand does not stop the run
- [ ] `docs/plan/next-action-and-runner.md` says the clean-up runs at the start of `chitty run`, before pending landings, under the landing lock, lists the reasons a merged branch is kept, and gives the `removed merged branch` and `kept merged branch` lines; `make check` passes

## Plan

At startup after setup refresh, under the landing lock, prune stale worktree registrations and remove merged local ticket branches before pending landings. Add focused real-Git runner tests covering deletion and every keep condition, update the runner plan, then format/check and commit implementation with Task trailer.

## Notes

Planning issue discovered: the required startup cleanup deletes every local ticket branch whose tip is contained by main, including branches for tickets already in review. The existing runner requires a branch/worktree to review and changes such tickets to error when missing; therefore a routine chitty run can delete the branch and then fail the same ticket during selection. The ticket does not specify whether such tickets should be exempt, returned to a workable status/recreated from main, or treated as an expected runner error. Existing runner tests also assume newly created equal-to-main ticket branches survive startup, so the required cleanup changes their expected behavior. Please decide the selection/review behavior after cleanup and update acceptance/tests accordingly.

Planning 2026-11-20: the review-state question in the earlier notes is resolved in the Description (keep merged branches of tickets that are not `done`). The branch's partial code predates it: it skips unknown IDs and has no status rule; fix both. Branch rebased onto `main` (old tip tagged `task-400-before-rebase`). Resumed as `doing` because the branch holds partial work.

## History

- 2026-11-18T18:00:02Z lively-quartz-crane → backlog
- 2026-11-18T18:00:04Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:00:04Z lively-quartz-crane backlog → cold-read
- 2026-11-18T18:02:13Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:02:13Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:02:15Z lively-quartz-crane planning → todo
- 2026-11-18T23:14:01Z golden-quartz-heron todo → doing
- 2026-11-18T23:15:19Z golden-quartz-heron: wrote the plan
- 2026-11-18T23:18:59Z golden-quartz-heron: changed owner, notes
- 2026-11-18T23:18:59Z golden-quartz-heron doing → planning
- 2026-11-20T23:19:59Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:19:59Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:24:27Z quick-pearl-lapwing: changed description, acceptance criteria, notes
- 2026-11-20T23:24:27Z quick-pearl-lapwing cold-read → doing
- 2026-11-20T23:25:08Z quick-pearl-lapwing: changed description
