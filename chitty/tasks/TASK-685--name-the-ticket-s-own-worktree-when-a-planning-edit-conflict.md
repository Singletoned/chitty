---
title: Name the ticket's own worktree when a planning edit conflicts with its branch
status: todo
created: 2026-11-24
---

## Description

### Why

On 2026-11-23, while planning TASK-358, TASK-599, TASK-629 and TASK-632 (all returned from `doing` to `planning` by workers), every edit from a `plan/<name>` worktree failed with `planning edit for TASK-358 conflicts with refs/heads/task-358`. Each ticket had its own `task-<n>` branch holding the newest copy. What worked was running `chitty edit` from that ticket's own worktree (`.worktrees/task-<n>`), but the error does not say so. The same happened on 2026-11-24 for TASK-599 and TASK-233.

### Change

In `Repo._reject_planning_conflicts` in `src/chitty/store.py` (around line 943), the refusal stays `planning edit for <ID> conflicts with <ref>`. When `<ref>` equals `refs/heads/{str(task_id).lower()}` exactly (the ticket's own branch, for example `refs/heads/task-358` or `refs/heads/task-fer4eb`; compare with that, not with the planning `branch` argument), append a hint:

- if `git.worktree_for_branch(self.root, str(task_id).lower())` returns a path: ``; edit it from its worktree `<path>` ``;
- otherwise: ``; edit it on branch `<own>` ``, where `<own>` is `str(task_id).lower()`.

Any other ref (`main`, another `plan/` branch, a remote) keeps today's message unchanged.

Put the wording in a pure function in `store.py`, `planning_conflict_message(task_id: TaskId, ref: str, worktree: Path | None) -> str`, which embeds `str(worktree)` exactly as given (no resolving, no escaping), and look up the worktree in `_reject_planning_conflicts` only for the ticket's own branch.

Decided: only the ticket's own branch gets a hint. For `main` or a sibling `plan/` branch the fix is a rebase or a merge, which this ticket does not try to advise.

### Tests

Property, with Hypothesis (this repository's property-testing tool), in a new `tests/test_planning_conflict_message.py`. Import the helpers with `from tests.test_property_ticket_source import decoy_names, task_ids`. Draw the ticket ID with `st.one_of(task_ids(), <suffix IDs>)`, where a suffix ID is `TaskId("TASK", provisional_suffix(lambda n: data.draw(st.integers(0, n - 1))))` (`provisional_suffix` from `chitty.ids` takes a draw callable, as in `tests/test_property_renumbering.py`), so IDs such as `TASK-FER4EB` occur. Draw the ref from: `refs/heads/<own>` where `<own>` is `str(task_id).lower()`; each local name from `decoy_names(task_id)` in the same file, as `refs/heads/<name>` (it includes the upper-case `str(task_id)` and `<own>0`); `refs/heads/main`; `refs/heads/plan/<word>`; and each remote name from `decoy_names` plus `origin/<own>`, as `refs/remotes/<name>`. Draw the worktree as `None` or `Path("/tmp") / name`, where `name` is drawn from `st.text(alphabet="abcXYZ019 é`", min_size=1, max_size=20)`. Then:

- the message always starts with `planning edit for <ID> conflicts with <ref>`;
- it contains ``; edit it from its worktree `<str(worktree)>` `` exactly when the ref is `refs/heads/<own>` and the worktree is not `None`;
- it contains ``; edit it on branch `<own>` `` exactly when the ref is `refs/heads/<own>` and the worktree is `None`;
- for every other ref it equals `planning edit for <ID> conflicts with <ref>`.

To show the property fails without the change, the worker temporarily makes `planning_conflict_message` return today's message unchanged, runs the property, records the failure in a note, and restores it. That only the ticket's own branch triggers the worktree lookup is covered by the example tests, not the property.

Example, in `tests/test_planning_worktrees.py`, extending `test_ticket_deletion_conflict` (which makes `task-1` with no worktree, then calls `assert_conflict("refs/heads/task-1")`): assert the stderr also contains ``edit it on branch `task-1` ``. A second example repeats the `test_ticket_deletion_conflict` setup (`switch -c task-1`, delete the ticket file, commit, `switch main`), then adds a worktree for `task-1` (`git worktree add <self.tmp>/task-1-tree task-1`, with `self.addCleanup(self.git, "worktree", "remove", "--force", <path>)` as the other worktree tests do) and asserts stderr contains ``edit it from its worktree `<path>` ``, comparing with `str(path.resolve())` because Git prints the real path (on macOS under `/private`); `self.tmp` is already resolved. `assert_conflict` checks for the old text with `assertIn`, so existing conflict tests keep passing.

### Out of scope

`git.worktree_for_branch` returning `None` when `git worktree list` fails (it catches `ChittyError`); that older behaviour has other callers and is left as it is.

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
- 2026-11-24T23:09:47Z zesty-coral-newt: changed description
- 2026-11-24T23:10:24Z zesty-coral-newt: changed description
- 2026-11-24T23:12:24Z zesty-coral-newt: changed description
- 2026-11-24T23:12:24Z zesty-coral-newt cold-read → todo
