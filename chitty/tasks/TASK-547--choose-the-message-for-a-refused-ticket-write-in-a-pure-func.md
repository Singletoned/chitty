---
title: Choose the message for a refused ticket write in a pure function
status: doing
parent: TASK-385
created: 2026-11-22
---

## Description

Split from `TASK-385` on 2026-11-22 so each part fits one worker session. Owner decisions 2026-11-22: a ticket write is refused only when another copy of the ticket is newer and differs from the copy this checkout would write over (so the write would be lost or hidden); where the ticket is read from does not otherwise matter, and identical copies never block a write. When it is refused, Chitty refuses (it does not apply the edit elsewhere), and the message says which newer copy the write would lose or hide and where to make the edit. `TASK-385` decides when to refuse; this ticket adds only the pure function that words the refusal. Nothing calls it yet.

Add to a new module `src/chitty/write_guard.py` (no imports from `chitty.store` or `chitty.run`):

`write_refusal(task_id: str, newer_ref: str, newer_sha: str, main_branch: str, local_branch: bool, worktree: Path | None, main_checkout: Path, checkout_is_main: bool, local_behind: bool) -> str`

- `newer_ref` is the branch holding the newer copy (`StoredTask.branch`, never `None` here), `newer_sha` the commit it was read from; the message shows `newer_sha[:10]`.
- `local_branch` says whether `newer_ref` names a local branch; `worktree` is the worktree that has `newer_ref` checked out, if any; `main_checkout` is the main checkout's path; `checkout_is_main` says whether the current checkout is the main checkout; `local_behind` says, for a remote-tracking `newer_ref`, whether a local branch of the same name exists (behind it).

Every message starts `f"{task_id} has a newer copy on {newer_ref} ({newer_sha[:10]}); "` and ends with what the user must do before or instead of editing here, by these rules in order:

1. `newer_ref == main_branch`: if `checkout_is_main`, `f"switch this checkout to {main_branch} first"`; else `f"edit it in the main checkout {main_checkout}"`.
2. `local_branch`: if `worktree` is not `None`, `f"edit it in worktree {worktree}"`; else `f"run git switch {newer_ref} first"`.
3. Otherwise `newer_ref` is a remote-tracking name `<remote>/<b>` (split at the first `/`): if `local_behind`, `f"fast-forward {b} to {newer_ref} first"`; else `f"run git switch --track {newer_ref} first"`.

Tests: Hypothesis (the repository's property tool) in a new `tests/test_property_write_guard.py`. Draw a ticket ID (`TASK-<n>`, `n` from 1 up), a main branch name from `st.sampled_from(["main", "master", "trunk"])`, a 40-hex SHA, and a case: the main name; a local name `task-<m>` (with `local_branch=True`); or `<remote>/task-<m>` with `<remote>` from `st.sampled_from(["origin", "upstream"])` (with `local_branch=False`); plus the other flags and paths (`Path` values built from drawn path parts). Draw every flag and path freely in every case. Expected message computed from the drawn values by the rules above, written out in the test, reading only the flags each rule reads (the others must not change the result); assert `write_refusal` returns it. The six literal examples are the independent check of the wording. Also one example per rule (six) with literal strings. Before implementing, add the function raising `NotImplementedError` and confirm the tests fail.

## Acceptance Criteria

- [ ] The property and the six per-rule examples pass, and fail against a `NotImplementedError` stub; `make check` passes

## Notes

Question for the owner (2026-11-22, overnight planner): `TASK-385` contradicts itself, so `TASK-547` (its pure message function) is parked. Its Decisions allow a write exactly when the ticket is read from this checkout's working tree (`stored.branch is None`), but its Description (your 2026-11-20 decision) also allows a write in the ticket's own fresh worktree when `main` has not changed the ticket since the split (`TASK-482`, done, implements that in today's guard), and says every refusal message must say which newer copy the write would lose or hide; the specified messages only say where to edit. Please confirm: (1) keep the own-fresh-worktree allowance (the caller computes it and the pure function gets an `own_fresh` flag)? (2) keep the five messages exactly as written, or add the newer copy (for example the ref and commit) to each? A cold reader also listed generator constraints for `TASK-547`, to apply once this is settled.

Planner, 2026-11-22: superseded by the owner answer on `TASK-385` (the rule is about a newer, different copy, not where the ticket is read from). Rewrite after the open question there is answered.

Owner decision, 2026-11-22: (A) refuse, naming the newer copy. Rewritten to match.

## History

- 2026-11-22T02:28:29Z lively-zinc-newt → cold-read
- 2026-11-22T02:28:39Z lively-zinc-newt: changed description
- 2026-11-22T02:30:03Z lively-zinc-newt: changed labels, notes
- 2026-11-22T02:30:03Z lively-zinc-newt cold-read → planning
- 2026-11-22T11:15:42Z friendly-jade-stoat: changed notes
- 2026-11-22T11:24:44Z friendly-jade-stoat: changed labels, description, acceptance criteria, notes
- 2026-11-22T11:24:44Z friendly-jade-stoat planning → cold-read
- 2026-11-22T11:25:44Z friendly-jade-stoat: changed description
- 2026-11-22T11:25:44Z friendly-jade-stoat cold-read → planning
- 2026-11-22T11:25:45Z friendly-jade-stoat planning → todo
- 2026-11-22T14:53:46Z golden-bronze-dormouse todo → doing
