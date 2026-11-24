---
title: Name the ticket's own worktree when a planning edit conflicts with its branch
status: cold-read
created: 2026-11-24
---

## Description

### Why

On 2026-11-23, while planning TASK-358, TASK-599, TASK-629 and TASK-632 (all returned from `doing` to `planning` by workers), every edit from a `plan/<name>` worktree failed with `planning edit for TASK-358 conflicts with refs/heads/task-358`. Each ticket had its own `task-<n>` branch holding the newest copy. What worked was running `chitty edit` from that ticket's own worktree (`.worktrees/task-<n>`), but the error does not say so. The same happened on 2026-11-24 for TASK-599 and TASK-233.

### Change

In `Repo._reject_planning_conflicts` in `src/chitty/store.py` (around line 943), the refusal stays `planning edit for <ID> conflicts with <ref>`. When `<ref>` is `refs/heads/<branch>` and `<branch>` is the ticket's own branch (`str(task_id).lower()`, for example `task-358`), append a hint:

- if `git.worktree_for_branch(self.root, branch)` returns a path: ``; edit it from its worktree `<path>` ``;
- otherwise: ``; edit it on branch `<branch>` ``.

Any other ref (`main`, another `plan/` branch, a remote) keeps today's message unchanged.

Put the wording in a pure function in `store.py`, `planning_conflict_message(task_id: TaskId, ref: str, worktree: Path | None) -> str`, and look up the worktree in `_reject_planning_conflicts` only for the ticket's own branch.

Decided: only the ticket's own branch gets a hint. For `main` or a sibling `plan/` branch the fix is a rebase or a merge, which this ticket does not try to advise.

### Tests

Property, with Hypothesis (this repository's property-testing tool), in `tests/test_planning_worktrees.py` or a new `tests/test_planning_conflict_message.py`: for any ticket number (1 to 9999), any ref drawn from `refs/heads/task-<n>` (the ticket's own), `refs/heads/task-<m>` with `m != n` (built from `n`, for example `n + 1`), `refs/heads/main`, `refs/heads/plan/<word>` and `refs/remotes/origin/task-<n>`, and a worktree of `None` or a drawn path:

- the message always starts with `planning edit for TASK-<n> conflicts with <ref>`;
- it contains `edit it from its worktree` exactly when the ref is the ticket's own local branch and the worktree is not `None`, and then contains the path;
- it contains ``edit it on branch `task-<n>` `` exactly when the ref is the ticket's own local branch and the worktree is `None`;
- for every other ref it equals `planning edit for TASK-<n> conflicts with <ref>`.

Example, in `tests/test_planning_worktrees.py`, extending `test_ticket_deletion_conflict` (which makes `task-1` with no worktree, then calls `assert_conflict("refs/heads/task-1")`): assert the stderr also contains ``edit it on branch `task-1` ``. A second example adds a worktree for `task-1` (`git worktree add <tmp>/task-1-tree task-1`) and asserts stderr contains ``edit it from its worktree `<that path>` ``. `assert_conflict` checks for the old text with `assertIn`, so existing conflict tests keep passing.

### Out of scope

Advice for conflicts with `main` or other branches; any change to when a conflict is reported; the plan guide's wording (a separate untestable ticket can add one line once this lands).

## Acceptance Criteria

- [ ] A new property test, as the Tests section describes, shows `planning_conflict_message` keeps today's text for every ref, adds ``edit it from its worktree `<path>` `` only for the ticket's own local branch with a worktree, and ``edit it on branch `task-<n>` `` only for that branch without one. It fails against a stub that returns today's message unchanged.
- [ ] In `tests/test_planning_worktrees.py`, `test_ticket_deletion_conflict` also asserts stderr contains ``edit it on branch `task-1` ``, and a new test with a worktree checked out on `task-1` asserts stderr contains ``edit it from its worktree `<path>` `` (paths compared after `.resolve()`). Both fail without the change; the other conflict tests pass unchanged, and `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:47Z zesty-coral-newt → backlog
- 2026-11-24T22:21:48Z zesty-coral-newt: changed notes
- 2026-11-24T23:08:08Z zesty-coral-newt: changed title, description, acceptance criteria
- 2026-11-24T23:08:08Z zesty-coral-newt backlog → cold-read
