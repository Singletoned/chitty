---
title: Tell work and repair agents to finish a stopped rebase
status: review
priority: high
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it; this is mechanical. Ticket files are merged mechanically too, because the branch's ticket commits carry the worker's progress. Only code conflicts go to an agent.

When the runner's rebase stops on a code conflict, the agent finishes it (`TASK-370` for work, `TASK-375` for review). It needs instructions. Nothing can be written to the ticket during a stopped rebase, so they come from the guide itself.

Decisions:

- New role file `src/chitty/roles/rebase.md`, printed by `chitty guide rebase <ID>`. It says: a rebase onto the integration branch stopped on conflicts; resolve each conflicted file keeping the intent of both sides; `git add` it; run `git -c core.editor=true rebase --continue`; repeat until no rebase is in progress; never run `git rebase --abort` or `--skip`; then run the configured setup and check commands and fix what the rebase broke. Keep it general (no repository-specific advice), as `AGENTS.md` requires of the guides.
- Add `rebase` to `ROLE_NAMES` in `src/chitty/store.py`, and to the role list in the `guide` command's help in `src/chitty/cli.py`; it takes a ticket ID like `work`.
- `guide()` in `src/chitty/store.py` gains a `directory: Path` argument (no default): the checkout whose state it reads. The CLI and MCP pass the current directory. The runner's `_agent_command` in `src/chitty/run.py` passes the ticket worktree, since the runner's own directory is the main checkout. This ticket makes that change, so `TASK-370` only relies on it.
- For roles `work` and `repair`, when `git.is_repository(directory)` and `git.rebase_in_progress(directory)` are both true, insert the `rebase` role text, followed by a blank line, directly after the `Work only on Chitty ticket <ID>.` line and before the role's usual text. Outside a repository there is no rebase, so nothing is added; any Git error inside a repository raises as usual.

Tests: in a new `tests/test_guide_rebase.py`, calling `guide()` and the CLI, with real repositories: a rebase stopped on a real conflict, with both backends (`rebase-merge` by default and `rebase-apply` with `git rebase --apply`), from the worktree root and from a subdirectory, and from a linked worktree; a clean repository; and a directory outside any repository. The oracle for "unchanged" is that, with no rebase in progress, the output equals the stopped-rebase output with the inserted rebase text and its blank line removed, and equals the output outside a repository. No property: a fixed set of states and two guides, all listed.

## Acceptance Criteria

- [x] `chitty guide rebase TASK-<n>` prints the `rebase` role text, which names `git rebase --continue` and forbids `--abort` and `--skip`
- [x] With a rebase stopped on a conflict (both backends, root and subdirectory, linked worktree), the work and repair guide output has the rebase text directly after the `Work only on Chitty ticket <ID>.` line; the test fails before the change
- [x] With no rebase in progress, or outside a repository, the work and repair guides equal the stopped-rebase output with the rebase text and its blank line removed
- [x] The runner passes the ticket worktree: a work run whose worktree has a stopped rebase gives the fake agent a prompt containing the rebase text, though the main checkout has none; `make check` passes

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

## Summary

Added exact linked-worktree placement coverage for work and repair. Fixed runner lookup of the conventional ticket worktree during a stopped rebase, when Git detaches HEAD and hides its branch from worktree-list. Added a fake-agent runner regression test proving the work prompt contains rebase instructions while main does not. Verified the regression fails without the fix, focused test passes, and make check passes (637 tests).

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
