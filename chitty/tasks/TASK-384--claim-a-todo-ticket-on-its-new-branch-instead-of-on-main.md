---
title: Claim a `todo` ticket on its new branch instead of on `main`
status: review
depends_on:
  - TASK-382
parent: TASK-376
created: 2026-11-18
---

## Description

Today `_run_ticket` in `src/chitty/run.py` claims a `todo` ticket on `main` (`main_repo.edit(action.id, Edit(status="doing", skip_verdicts=True, skip_current_version=True))`, from `TASK-372`) and only then makes or reuses its worktree. Under the new ticket state model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`) the ticket branch is the ticket while it exists, and the runner writes nothing on `main` for it. "Queued" means `todo` on `main` with no ticket branch, so making the branch is the claim. This reverses `TASK-372`'s claim on `main`.

Starts after `TASK-382` (`branch_repo`) lands. It lands before `TASK-378` switches reads to the decided rule: today's reads already show the branch's newer claim as `doing` in the main checkout (the newest copy across refs wins), and under the rule the branch copy is authoritative, so criterion 1 holds either way. Claiming on `main` while a ticket branch exists is what made `TASK-378`'s new reads see that ticket as changed on both sides.

Decisions:

- In work mode, for a ticket chosen as `todo`: call `_worktree` first (it makes `task-<n>` from `main`, or reuses the existing branch), then claim in the worktree through a `Repo` built on it (the `branch_repo = Repo(worktree, main_repo.config)` that `_run_ticket` already makes after `_worktree`) with `Edit(status="doing", skip_verdicts=True, skip_current_version=True)`, then `setup` and `check` as today. Remove the claim on `main`. `doing` and `error` tickets are not claimed, as today.
- `main`'s committed copy stays `todo`; reads in the main checkout show `doing` from the branch.
- A `_worktree` failure before the claim leaves the ticket `todo` with nothing written, so the next run tries again. A worktree with an unfinished rebase makes `_worktree` raise this way; today the claim on `main` lands first and leaves the ticket stuck in `doing`.
- The uncommitted-changes guard (today `git.dirty_paths` on `main`'s ticket file, for every mode) moves to the ticket's worktree file, still for every mode and still before `_worktree`: when `git.worktree_for_branch(main_root, "task-<n>")` returns a path, an uncommitted change to its ticket file raises `ChittyError` naming that worktree path, and nothing is created or written; with no worktree there is nothing to check. The run no longer writes `main`'s file, so `main` needs no guard.
- If the claim itself fails after `_worktree`, the branch stays, the ticket is still `todo` on it (so `todo` by the rule), and the error propagates unrecorded (no `context["phase"]` is set yet, so the outer handler records nothing); the next run selects it again and reuses the branch. Selection already picks any `todo` ticket wherever it is read from. Do not edit `docs/plan/ticket-state.md`: it is only on branch `plan/ticket-state`, and its "queued" line is corrected there, not here.
- `test_run_check_failure_on_todo_ticket_records_error_on_branch` in `tests/test_next.py` (from `TASK-423`) asserts that `main`'s ticket says `status: doing` and that `main` gains exactly the claim commit (`main_ticket_commits == ["chitty: edit TASK-1 Todo"]`). Change it to assert that `git rev-parse main` is unchanged, `main`'s ticket still says `status: todo`, and the first commit on `task-1` after `main` is the claim; keep its other assertions.
- The check-failure rule still keys on the status the ticket had when the run chose it (`selected_status`), as `TASK-372` made it.
- In `docs/plan/next-action-and-runner.md`, replace "claims a `todo` ticket in the main checkout, then makes or reuses its worktree and runs `setup` there" with "makes or reuses a ticket's worktree, claims a `todo` ticket on its branch, then runs `setup` there", and "Work mode claims a `todo` ticket in the main checkout before preparing the worktree, then runs `setup` and `check`" with "Work mode makes or reuses the worktree and claims a `todo` ticket on its branch, then runs `setup` and `check`".

Tests: real-Git, fake-agent runner tests. Replace `tests/test_run_claims_on_main.py` with `tests/test_run_claims_on_branch.py` in the same style (it inherits `CliTestCase` from `tests/test_cli.py`); the fake agent records the ticket status it sees in the worktree in a marker file. No property: one fixed ordering change in a runner that drives real Git and agent processes, over the cases listed in the criteria.

## Acceptance Criteria

- [ ] A work run on a `todo` ticket with no branch leaves `git rev-parse main` unchanged and `main`'s committed ticket at `todo`; the first commit on `task-<n>` after `main` is the claim (`todo → doing`); the fake agent records `doing`; `chitty show <ID>` in the main checkout reports `doing`; the test fails before the change
- [ ] A work run on a `todo` ticket whose branch already exists (made with `git branch task-<n> main`, then a note added in its worktree with `git worktree add .worktrees/task-<n> task-<n>` and `chitty edit --note` there, status still `todo`) leaves `main` unchanged, makes the claim the newest commit on that branch before the agent starts, keeps the note, and starts the agent
- [ ] A ticket chosen as `todo` whose `setup` fails, and one whose `check` fails, both end `error` on the branch with no agent started and `main` unchanged; each fails before the change
- [ ] A `todo` ticket whose existing worktree has a rebase stopped on a conflict (a commit on `main` and one on the branch changing the same line of a code file, then `git rebase main` in the worktree): the run fails, and the ticket is `todo` on both `main` and the branch (fails before the change). A `todo` ticket whose worktree has an uncommitted edit to its ticket file, with `main`'s file clean: the run fails naming the worktree file and creates or commits nothing (fails before the change, which checks only `main`'s file and claims)
- [ ] Regression guard: `test_run_check_failure_on_doing_ticket_starts_agent` in `tests/test_next.py` still passes unchanged; `test_run_check_failure_on_todo_ticket_records_error_on_branch` in `tests/test_next.py` asserts no commit on `main` and the claim as the first commit on `task-1`; `docs/plan/next-action-and-runner.md` has the two replacement sentences (lines 56 to 57 and 126 to 127 today); `make check` passes

## Plan

Move the dirty-ticket guard to an existing ticket worktree and claim todo only after worktree creation using its Repo. Replace the real-Git runner regressions, update the existing check-failure test and runner plan, verify the regressions fail before the fix, then run fix, format and checks.

## Notes

Planner, 2026-11-20: both questions in the earlier return are settled in the Description: `docs/plan/ticket-state.md` is not edited here, and the test to change is `test_run_check_failure_on_todo_ticket_records_error_on_branch` in `tests/test_next.py`.

Before the fix, the new real-Git tests failed for the new branch, existing branch, setup failure, unfinished rebase and dirty ticket because main gained the claim commit. The combined check-failure subcase inherited the first failure; it is being isolated before verifying that regression separately.

The isolated check-failure regression also fails before the fix because main gains the claim commit.

Existing runner tests also assumed a main claim; updated them to assert branch-only behaviour. The check-failure fixture needed init before its baseline because automatic setup refresh otherwise creates a separate main commit.

## Summary

The runner checks an existing worktree for a dirty ticket and claims todo on its branch before setup. Real-Git regressions cover new and existing branches, setup and check failures, rebase conflicts and dirty tickets; they failed before the change. Updated existing runner tests and the runner plan. Verification: chitty fix, make format and make check (807 tests) passed. No follow-ups.

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
- 2026-11-20T13:05:49Z eager-hazel-dormouse todo → doing
- 2026-11-20T13:06:46Z eager-hazel-dormouse: changed notes
- 2026-11-20T13:06:46Z eager-hazel-dormouse doing → error
- 2026-11-20T17:23:07Z jolly-dusky-badger: replaced notes
- 2026-11-20T17:23:07Z jolly-dusky-badger error → todo
- 2026-11-20T17:23:18Z sunny-fawn-dormouse todo → doing
- 2026-11-20T17:24:09Z sunny-fawn-dormouse: changed notes
- 2026-11-20T17:24:09Z sunny-fawn-dormouse doing → error
- 2026-11-20T17:30:48Z jolly-dusky-badger: replaced notes
- 2026-11-20T17:30:48Z jolly-dusky-badger error → todo
- 2026-11-20T17:31:09Z intrepid-indigo-falcon todo → doing
- 2026-11-20T17:34:04Z intrepid-indigo-falcon: changed owner, notes
- 2026-11-20T17:34:04Z intrepid-indigo-falcon doing → planning
- 2026-11-20T17:36:52Z jolly-dusky-badger: replaced notes; changed owner, description, acceptance criteria
- 2026-11-20T17:36:52Z jolly-dusky-badger planning → cold-read
- 2026-11-20T17:37:55Z jolly-dusky-badger: changed description, acceptance criteria
- 2026-11-20T17:37:55Z jolly-dusky-badger cold-read → todo
- 2026-11-20T17:39:42Z able-violet-lapwing todo → doing
- 2026-11-20T17:42:24Z able-violet-lapwing: wrote the plan
- 2026-11-20T17:43:33Z able-violet-lapwing: changed notes
- 2026-11-20T17:43:53Z able-violet-lapwing: changed notes
- 2026-11-20T17:46:45Z able-violet-lapwing: changed notes
- 2026-11-20T17:47:45Z able-violet-lapwing: changed summary
- 2026-11-20T17:47:48Z able-violet-lapwing doing → review
