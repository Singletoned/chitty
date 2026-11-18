---
title: Tell work and repair agents to finish a stopped rebase
status: doing
priority: high
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

When the runner's rebase stops on a code conflict, the agent finishes it (`TASK-370` for work, `TASK-375` for review). It needs instructions. Nothing can be written to the ticket during a stopped rebase, so they come from the guide itself.

Decisions:

- New role file `src/chitty/roles/rebase.md`, printed by `chitty guide rebase <ID>`. It says: a rebase onto the integration branch stopped part-way, usually on conflicts (any rebase in progress gets this text, including one a person stopped; accepted); resolve each conflicted file keeping the intent of both sides; `git add` it; run `git -c core.editor=true rebase --continue`; repeat until no rebase is in progress; never run `git rebase --abort` or `--skip`; then run the configured setup and check commands and fix what the rebase broke. Keep it general (no repository-specific advice), as `AGENTS.md` requires of the guides. Give one continue command, not two.
- Add rebase where the roles are listed: `README.md` (the sentence on roles that take an optional ticket ID) and `docs/plan/agent-instructions.md`.
- Add `rebase` to `ROLE_NAMES` in `src/chitty/store.py`. In the `guide` command's help in `src/chitty/cli.py`, add the example `chitty guide rebase TASK-12`, and add rebase to the sentence listing roles that accept an optional ticket ID.
- `guide()` in `src/chitty/store.py` gains a `directory: Path` argument (no default): the checkout whose state it reads. The CLI passes the current directory. MCP has no role-guide entry point (`src/chitty/mcp.py`), so it needs no change. The runner's `_agent_command` in `src/chitty/run.py` keeps its signature; its two `guide()` calls pass `directory=repo.root`, the main checkout, where the runner builds the prompt today, so the runner's prompts are unchanged. Giving the runner the ticket worktree is `TASK-370`'s, which renders the prompt again after its own rebase stops (split out 2026-11-18). Every existing test call to `guide()` passes a directory, such as the test repository's root (`git grep -n 'guide(' tests` finds them).
- On this branch, revert `allow_rebase` in `_worktree`, `git.rebasing_branch`, `git._git_dir_path`, and every other change to `src/chitty/run.py` and `src/chitty/git.py` beyond passing `repo.root` to `guide()`; remove `test_worktree_for_another_branch_is_rejected` and `test_stopped_ticket_rebase_is_included_in_work_prompt` from `tests/test_run_continue.py`. (Planning 2026-11-18: an earlier criterion 4 implied a run should reach the agent with a leftover rebase; it should not.)
- For roles `work` and `repair`, when `git.is_repository(directory)` and `git.rebase_in_progress(directory)` are both true, insert the `rebase` role text, followed by a blank line, directly after the `Work only on Chitty ticket <ID>.` line and before the role's usual text. Outside a repository, or in a directory that does not exist (`git.is_repository` returns false for both), there is no rebase, so nothing is added; any Git error inside a repository raises as usual.

Tests: in a new `tests/test_guide_rebase.py`, calling `guide()` and the CLI, with real repositories: a rebase stopped on a real conflict, with both backends (`rebase-merge` by default and `rebase-apply` with `git rebase --apply`), from the worktree root and from a subdirectory, and from a linked worktree; a clean repository; a temporary directory outside any repository (the test asserts `git rev-parse --is-inside-work-tree` fails there); and a directory that does not exist. Also during a stopped rebase, the review, plan and cold-read guides equal their output with no rebase. The oracle for "unchanged" is that, with no rebase in progress, the output equals the stopped-rebase output with the inserted rebase text (the body of `src/chitty/roles/rebase.md`) and its blank line removed, and equals the output outside a repository. No property: a fixed set of states and two guides, all listed.

## Acceptance Criteria

- [ ] `chitty guide rebase TASK-<n>` prints the `rebase` role text, which names `git rebase --continue` and forbids `--abort` and `--skip`
- [ ] With a rebase stopped on a conflict (both backends, root and subdirectory, linked worktree), the work and repair guide output has the rebase text directly after the `Work only on Chitty ticket <ID>.` line; evidence of failing without the change is these tests failing on the rebase-text assertion with injection disabled (for example `git.rebase_in_progress` patched to return false), not a `TypeError` on `main`
- [ ] With no rebase in progress, outside a repository, or in a directory that does not exist, the work and repair guides equal the stopped-rebase output with the rebase text and its blank line removed; during a stopped rebase, the review, plan and cold-read guides equal their output with no rebase in progress
- [ ] The runner and Git helpers are unchanged apart from passing `directory=repo.root` to `guide()`: `git diff main -- src/chitty/run.py src/chitty/git.py` shows only that, and `git diff main -- tests/test_run_continue.py` adds no test that mentions a rebase; `make check` passes

## Plan

Add a general rebase role and inject it into work/repair guide output only when the supplied checkout is inside an active rebase. Thread the current directory through CLI/MCP and the ticket worktree through runner prompts. Add real-repository tests covering both rebase backends and location variants plus unchanged-output cases and runner prompt behavior. Run regression tests before implementation to verify failure, then make check and commit implementation.

## Notes

The new guide tests failed initially because the rebase role did not expose the exact continuation command wording; corrected the role and reran the focused tests. Rebase detection must use the ticket worktree, not main: the runner now selects that path before producing the prompt and allows a stopped rebase only on the work-agent startup path, while pending landing still rejects it.

Review failed (tests): Newly discovered coverage gaps must be addressed; there are no earlier review failures.
1: pass - `uv run python -m unittest tests.test_guide_rebase -v` printed OK; the CLI test and role text cover continuation and both prohibitions.
2: fail - The focused tests printed OK and disabling `chitty.store.git.rebase_in_progress` made the backend injection test print FAILED (failures=2). However, `test_linked_worktree_detects_its_stopped_rebase` exercises only work, not repair, and checks only a substring rather than the required placement. Exercise both roles and placement in the linked worktree.
3: pass - The focused test printed OK for both roles, comparing clean and outside-repository output with stopped-rebase output minus the insertion.
4: fail - `make check` printed OK (632 tests), but no test runs a fake agent with a stopped rebase in the ticket worktree while main is clean. Add that runner regression test and show it fails without the change.

Regression evidence: the linked-worktree test now checks exact insertion placement for both work and repair. The runner regression test failed without the fix: a stopped rebase detached HEAD, so Git no longer reported the ticket branch in worktree-list and the runner tried to add an already-existing worktree. After returning the conventional ticket worktree path when it exists, the fake agent received rebase instructions while main did not. Verified focused test and make check (637 tests).

Review failed (work): Newly discovered worktree identity defect; the earlier review coverage gaps are resolved.
1: pass - `uv run python -m unittest tests.test_guide_rebase -v` printed OK; the role names continuation and forbids abort and skip.
2: pass - The focused tests printed OK for both roles and linked-worktree placement; patching `chitty.store.git.rebase_in_progress` to return false printed FAILED (failures=3), including both backends and the linked worktree.
3: pass - The focused tests printed OK for clean and outside-repository output comparisons.
4: fail - `make check` printed OK (637 tests), and the fake-agent rebase test passed. However, a throwaway test using `TestRunContinue` created a conventional task-1 worktree on branch other and called `_worktree` with task-1; it printed `requested: task-1 returned branch: other`. The new unconditional return accepts an unrelated checkout and can send the agent to the wrong branch. Verify the worktree belongs to the ticket, including detached rebase identity, before returning it; reject mismatches and add regression coverage.

Review failed (work): Newly discovered worktree identity defect; earlier review gaps were resolved.\n1: pass - `uv run python -m unittest tests.test_guide_rebase -v` plus CLI role assertions verify continuation and both prohibitions.\n2: pass - Focused tests exercise both backends, both roles, root/subdirectory, linked worktree placement; disabling rebase detection makes them fail.\n3: pass - Focused tests compare clean and outside-repository output with stopped-rebase output minus insertion.\n4: fail - `make check` printed OK (637 tests), including the fake-agent stopped-rebase prompt test. However, a throwaway Python invocation created a valid conventional worktree at `.worktrees/task-1` on branch `task-1`, then called `_worktree` for `TASK-1` with `allow_rebase=True`; it returned that worktree even though no rebase was active. The unconditional conventional-path return bypasses verifying the worktree belongs to the requested ticket, reproducing the prior review finding. Validate ticket identity (including detached HEAD during rebase) before returning the path and add a mismatched-worktree regression test.

Follow-up: `make check` passed (642 tests), including the mismatched conventional-worktree regression and stopped-rebase fake-agent prompt test. A throwaway reproducer of the previous defect returned the wrong worktree before the fix; afterward the regression test verifies rejection. The original runner prompt behavior remains passing.

Review failed (design): Newly discovered ticket/code mismatch: the description says MCP passes the current directory to role-specific `guide()`, but `src/chitty/mcp.py` exposes only the repository-wide `chitty://guide` resource and never calls `guide()`. There is no existing MCP role-guide entry point to update. Decide whether MCP needs a new role-guide interface and acceptance coverage, or remove that requirement; the ticket cannot guide that part of the work as written. Earlier review findings about linked-worktree coverage and worktree identity are resolved by the focused tests.
1: fail - The CLI role test printed OK, but the associated MCP requirement has no existing role-guide entry point; decide its intended scope.
2: pass - Focused tests printed OK for both backends, directories and linked worktree; patching rebase detection false printed FAILED (failures=2).
3: pass - Focused tests printed OK for clean and outside-repository output comparisons.
4: pass - The fake-agent stopped-rebase and mismatched-worktree tests printed OK; the earlier note records the runner test failing before the fix. `make check` printed OK (642 tests).

Planning 2026-11-18: removed the requirement that MCP passes the current directory to `guide()`; `src/chitty/mcp.py` has no role-guide entry point. Nothing else changed; the implementation on this branch stands. Fits the one-authoritative-copy model (`docs/plan/ticket-state.md`).

Review failed (work): Newly discovered nonconventional worktree defect; earlier linked-worktree coverage and conventional worktree identity findings were resolved.
1: pass - `uv run python -m unittest tests.test_guide_rebase -v` printed OK; the CLI exposes the role and its text requires continuation and forbids abort and skip.
2: pass - The focused tests printed OK for both roles, both backends, root, subdirectory and linked worktree; the earlier review recorded FAILED (failures=3) with rebase detection disabled.
3: pass - The focused tests printed OK comparing stopped-rebase output minus insertion to clean and outside-repository output for both roles.
4: fail - `make check` printed OK (642 tests), including the conventional worktree fake-agent test; the worker recorded that test failing before the fix. A throwaway invocation based on `TestRunContinue` created a ticket branch in a linked worktree at `custom`, stopped a real conflicting rebase there, and ran `chitty run --ticket TASK-1`. It exited 1 with `fatal: 'task-1' is already used by worktree at .../repo/custom` instead of invoking the agent. Git reports detached HEAD during rebase, so branch lookup misses nonconventional worktrees and the conventional-path fallback creates another checkout. Locate the rebasing ticket worktree by its recorded branch identity regardless of path, use it for the prompt and add a regression test.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Planning 2026-11-18, after three failed reviews: the reviews found real defects, but in code the ticket should never have needed. Criterion 4 asked a work run to reach the agent while the worktree held a stopped rebase, which `_worktree` on `main` refuses, so the worker loosened it (`allow_rebase`, `git.rebasing_branch`) and each review found a new gap in that lookup. In the real flow `TASK-370` and `TASK-375` start the agent after their own rebase stops and never go through that check. Decision: revert `allow_rebase` and `git.rebasing_branch`, keep the rest of the implementation, and test `_agent_command` directly. Criteria 1 to 3 stand.

Cold read 2026-11-18 outcomes: accepted the detached-worktree lookup gap (documented as accepted, `TASK-370` re-renders from the rebased worktree), the missing-directory case, the conventional path and `doing` start for the refusal test, the failing-on-main wording, and the help wording. Rejected a runner test that patches `chitty.run._worktree`: it mocks our own code, and the end-to-end path belongs to `TASK-370`.

Second cold read 2026-11-18 outcomes: accepted the test file for criterion 4, naming `TASK-370` as the end-to-end check, an explicit `is_dir()` check, other roles unchanged during a rebase, and naming the branch tests to replace. Kept the rebase role ID and prefix as built (criterion 1 is met).

Third cold read 2026-11-18 found two serious problems, both in the runner half: the `is_dir()` rationale from the previous round was wrong (`git.is_repository` already returns false for a missing directory, and for a missing `git`, which this ticket leaves alone), and criterion 4 would fail on `main` with a `TypeError`, not its assertion. Per the third-read rule, split: the runner now passing the worktree moves to `TASK-370`, which already renders the prompt from its rebased worktree. This ticket is the guide work, criteria 1 to 3, mostly built.

Fourth cold read 2026-11-18 outcomes: kept `_agent_command` signature here (`TASK-370` adds `directory`); fails-before evidence by disabling injection rather than a `TypeError`; checkable wording for criterion 4; role text says part-way; README and `docs/plan/agent-instructions.md` added. Unticked criteria 1 and 2: the branch tests check only that `--abort` and `--skip` appear, not that they are forbidden, and the linked worktree only with one backend. Code gaps for the worker, not ticket changes: criterion 3 tests for other roles, the missing directory and the outside check are not written yet; the help line alignment.

## Summary

Implemented stopped-rebase guidance for work and repair agents, with runner prompts using the ticket worktree. Added coverage for both rebase backends, linked worktrees, clean/outside repositories, and mismatched worktree identity. Verification: `make check` passed all 642 tests; `chitty fix` completed with existing warnings in unrelated task files. Follow-ups: none.

## History

- 2026-11-18T09:50:54Z witty-ginger-falcon → planning
- 2026-11-18T09:52:32Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:55:11Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:55:13Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:55:15Z witty-ginger-falcon planning → todo
- 2026-11-18T11:08:04Z lively-maroon-crane todo → doing
- 2026-11-18T11:08:56Z lively-maroon-crane: wrote the plan
- 2026-11-18T11:19:14Z lively-maroon-crane: changed notes, summary; ticked acceptance criteria
- 2026-11-18T11:19:14Z lively-maroon-crane doing → review
- 2026-11-18T11:21:53Z tidy-silver-quail: changed acceptance criteria, notes
- 2026-11-18T11:21:53Z tidy-silver-quail review → doing
- 2026-11-18T11:29:52Z youthful-indigo-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-18T11:30:01Z youthful-indigo-ibis doing → review
- 2026-11-18T11:32:49Z eager-ebony-crane: changed acceptance criteria, notes
- 2026-11-18T11:32:49Z eager-ebony-crane review → doing
- 2026-11-18T11:35:03Z zesty-khaki-vole: changed acceptance criteria, notes
- 2026-11-18T11:37:55Z zesty-khaki-vole: changed notes, summary; ticked acceptance criteria
- 2026-11-18T11:37:55Z zesty-khaki-vole doing → review
- 2026-11-18T11:40:57Z witty-maroon-newt: changed owner, acceptance criteria, notes
- 2026-11-18T11:40:57Z witty-maroon-newt review → planning
- 2026-11-18T16:30:36Z lively-quartz-crane: changed description, notes
- 2026-11-18T16:30:56Z lively-quartz-crane planning → todo
- 2026-11-18T19:52:23Z tidy-pearl-falcon todo → doing
- 2026-11-18T19:59:24Z tidy-pearl-falcon: changed summary; ticked acceptance criteria
- 2026-11-18T19:59:24Z tidy-pearl-falcon doing → review
- 2026-11-18T20:02:27Z honest-teal-quail: changed owner, acceptance criteria, notes
- 2026-11-18T20:02:27Z honest-teal-quail review → blocked
- 2026-11-18T20:37:13Z lively-quartz-crane: changed owner, description, acceptance criteria, notes
- 2026-11-18T20:37:13Z lively-quartz-crane blocked → planning
- 2026-11-18T20:37:38Z lively-quartz-crane planning → cold-read
- 2026-11-18T20:39:50Z lively-quartz-crane: changed description, acceptance criteria, notes
- 2026-11-18T20:39:50Z lively-quartz-crane cold-read → planning
- 2026-11-18T20:40:10Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T20:40:10Z lively-quartz-crane planning → cold-read
- 2026-11-18T20:41:48Z lively-quartz-crane: changed description, acceptance criteria, notes
- 2026-11-18T20:41:48Z lively-quartz-crane cold-read → planning
- 2026-11-18T20:41:52Z lively-quartz-crane planning → cold-read
- 2026-11-18T20:44:10Z lively-quartz-crane: changed description, acceptance criteria, notes
- 2026-11-18T20:44:10Z lively-quartz-crane cold-read → planning
- 2026-11-18T20:47:46Z lively-quartz-crane planning → todo
- 2026-11-18T20:49:48Z lively-quartz-crane todo → planning
- 2026-11-18T20:51:08Z lively-quartz-crane: changed description, acceptance criteria, notes
- 2026-11-18T20:51:10Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T20:51:14Z lively-quartz-crane planning → todo
- 2026-11-18T21:58:55Z youthful-bronze-gannet todo → doing
