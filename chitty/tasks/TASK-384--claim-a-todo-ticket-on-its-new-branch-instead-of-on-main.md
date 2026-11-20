---
title: Claim a `todo` ticket on its new branch instead of on `main`
status: todo
depends_on:
  - TASK-382
parent: TASK-376
created: 2026-11-18
---

## Description

Today `_run_ticket` in `src/chitty/run.py` claims a `todo` ticket on `main` (`main_repo.edit(action.id, Edit(status="doing", skip_verdicts=True, skip_current_version=True))`, from `TASK-372`) and only then makes or reuses its worktree. Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) the ticket branch is the ticket while it exists, and the runner writes nothing on `main` for it. "Queued" means `todo` on `main` with no ticket branch, so making the branch is the claim. This reverses `TASK-372`'s claim on `main`.

Starts after `TASK-382` (`branch_repo`) lands. It lands before `TASK-378` switches reads to the decided rule: today's reads already show the branch's newer claim as `doing` in the main checkout (the newest copy across refs wins), and under the rule the branch copy is authoritative, so criterion 1 holds either way. Claiming on `main` while a ticket branch exists is what made `TASK-378`'s new reads see that ticket as changed on both sides.

Decisions:

- In work mode, for a ticket chosen as `todo`: call `_worktree` first (it makes `task-<n>` from `main`, or reuses the existing branch), then claim in the worktree through `branch_repo` with `Edit(status="doing", skip_verdicts=True, skip_current_version=True)`, then `setup` and `check` as today. Remove the claim on `main`. `doing` and `error` tickets are not claimed, as today.
- `main`'s committed copy stays `todo`; reads in the main checkout show `doing` from the branch.
- A `_worktree` failure before the claim leaves the ticket `todo` with nothing written, so the next run tries again. A worktree with an unfinished rebase makes `_worktree` raise this way; today the claim on `main` lands first and leaves the ticket stuck in `doing`.
- The uncommitted-changes guard (today `git.dirty_paths` on `main`'s ticket file, for every mode) moves to the ticket's worktree file, still for every mode and still before `_worktree`: when a worktree for `task-<n>` already exists, an uncommitted change to its ticket file raises `ChittyError` naming that worktree path, and nothing is created or written; with no worktree there is nothing to check. The run no longer writes `main`'s file, so `main` needs no guard.
- If the claim itself fails after `_worktree`, the branch stays, the ticket is still `todo` on it (so `todo` by the rule), and the error propagates unrecorded; the next run selects it again and reuses the branch. Selection already picks any `todo` ticket wherever it is read from, so in `docs/plan/ticket-state.md` "queued" means `todo` tickets, whether or not they have a branch; correct that line there too.
- `TASK-382`'s test for a `check` failure on a `todo` ticket (in `tests/test_run_errors_on_branch.py`) expects `main` to gain the claim commit; change it to expect no commit on `main` and the claim as the first commit on `task-<n>`.
- The check-failure rule still keys on the status the ticket had when the run chose it (`selected_status`), as `TASK-372` made it.
- In `docs/plan/next-action-and-runner.md`, replace "claims a `todo` ticket in the main checkout, then makes or reuses its worktree and runs `setup` there" with "makes or reuses a ticket's worktree, claims a `todo` ticket on its branch, then runs `setup` there", and "Work mode claims a `todo` ticket in the main checkout before preparing the worktree, then runs `setup` and `check`" with "Work mode makes or reuses the worktree and claims a `todo` ticket on its branch, then runs `setup` and `check`".

Tests: real-Git, fake-agent runner tests. Replace `tests/test_run_claims_on_main.py` with `tests/test_run_claims_on_branch.py` in the same style (it inherits `CliTestCase` from `tests/test_cli.py`); the fake agent records the ticket status it sees in the worktree in a marker file. No property: one fixed ordering change in a runner that drives real Git and agent processes, over the cases listed in the criteria.

## Acceptance Criteria

- [ ] A work run on a `todo` ticket with no branch leaves `git rev-parse main` unchanged and `main`'s committed ticket at `todo`; the first commit on `task-<n>` after `main` is the claim (`todo → doing`); the fake agent records `doing`; `chitty show <ID>` in the main checkout reports `doing`; the test fails before the change
- [ ] A work run on a `todo` ticket whose branch already exists (made with `git branch task-<n> main`, then a note added in its worktree with `git worktree add .worktrees/task-<n> task-<n>` and `chitty edit --note` there, status still `todo`) leaves `main` unchanged, makes the claim the newest commit on that branch before the agent starts, keeps the note, and starts the agent
- [ ] A ticket chosen as `todo` whose `setup` fails, and one whose `check` fails, both end `error` on the branch with no agent started and `main` unchanged; each fails before the change
- [ ] A `todo` ticket whose existing worktree has a rebase stopped on a conflict (a commit on `main` and one on the branch changing the same line of a code file, then `git rebase main` in the worktree): the run fails, and the ticket is `todo` on both `main` and the branch (fails before the change); a `todo` ticket whose worktree has an uncommitted edit to its ticket file: the run fails naming the worktree file and creates or commits nothing
- [ ] Regression guard: a `doing` ticket whose `check` fails still starts the agent; `TASK-382`'s `todo` check-failure test expects no commit on `main`; `docs/plan/next-action-and-runner.md` has the two replacement sentences; `make check` passes

## History

- 2026-11-18T16:20:14Z lively-quartz-crane → backlog
- 2026-11-18T16:23:21Z lively-quartz-crane: changed dependencies
- 2026-11-18T16:33:47Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T16:33:47Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:32Z lively-quartz-crane planning → cold-read
- 2026-11-18T16:43:26Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T16:43:26Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:44:49Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:47:26Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:47:26Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:47:28Z lively-quartz-crane planning → todo
- 2026-11-20T12:42:17Z jolly-dusky-badger: changed dependencies, description
