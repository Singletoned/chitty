---
title: Add a helper that rebases a work worktree onto `main`, keeping uncommitted work
status: todo
labels:
  - bug
priority: high
depends_on:
  - TASK-373
  - TASK-374
  - TASK-384
  - TASK-382
  - TASK-534
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`): `main` is the base every ticket branch builds on, and the runner rebases the branch onto `main` whenever it touches it. Work mode never does today, so workers build on code behind `main` (seen 2026-11-21: `task-519` was 120 commits behind and missed a function its ticket relied on).

Split 2026-11-22, after the worker model gave up on larger versions three times. This ticket adds only the helper and tests it directly; `TASK-546` calls it from the runner for `doing` tickets; `TASK-545` extends that to `todo` and `error`; `TASK-540` hands a conflict to the agent; `TASK-541` records a non-conflict failure; `TASK-525` reports saved work that cannot be restored.

Add `_rebase_work_worktree(worktree: Path, task_id: TaskId, main_branch: str) -> None` in `src/chitty/run.py`, with `ref = f"refs/chitty/stash/{task_id}"`. Nothing calls it yet.

1. `saved = git.save_work(worktree, ref, f"chitty {task_id} before rebase")`; its `ChittyError` propagates.
2. `unresolved = git.rebase_onto(worktree, main_branch)`. If that raises `ChittyError`, call `git.restore_work(worktree, ref)` when `saved`, then re-raise.
3. If `unresolved` is non-empty (stopped on a conflict), call `git.abort_rebase(worktree)`, so the branch stays as it was.
4. If `saved`, call `git.restore_work(worktree, ref)` and ignore its result.

`git.save_work`, `git.restore_work`, `git.rebase_onto` and `git.abort_rebase` exist in `src/chitty/git.py` (rechecked 2026-11-22).

Tests in a new `tests/test_rebase_work_worktree.py`, a `unittest.TestCase` like `SavedWorkTests` in `tests/test_git_saved_work.py`, with no runner: a temporary repository (`git init -b main`, local author, committed `a.txt` and `b.txt`), a branch `task-1` with one commit changing `b.txt`, checked out in a linked worktree via `git worktree add`, and then a commit on `main` changing `a.txt`. Call `_rebase_work_worktree(worktree, TaskId("TASK", 1), "main")` directly.

1. Clean: afterwards `git merge-base --is-ancestor main task-1` succeeds and `git rev-list main..task-1` has one commit.
2. Saved work: before the call, the worktree has an unstaged edit to `b.txt`, a staged new file `s.txt` and an untracked `u.txt`. Afterwards the branch is rebased as in 1, all three files have their pre-call contents (contents only; `s.txt` may come back unstaged), and `refs/chitty/stash/TASK-1` does not exist.
3. Conflict: build the fixture with `task-1`'s commit changing line 1 of `a.txt` instead of `b.txt` (so it conflicts with `main`'s commit), and put an untracked `u.txt` in the worktree before the call. Afterwards no rebase is in progress (`git.rebase_in_progress`), the `task-1` tip is unchanged, `u.txt` has its contents, and the ref does not exist.
4. Failure: with `chitty.run.git.rebase_onto` patched to raise `ChittyError("boom")` and an untracked `u.txt` present, the call raises `boom`, `u.txt` has its contents, and the ref does not exist.

Before implementing, add the function raising `NotImplementedError` and confirm the four tests fail; then implement and run `make check`.

## Acceptance Criteria

- [ ] The four helper tests pass, and each errors with `NotImplementedError` against a stub
- [ ] `make check` passes

## Plan

Build the five prescribed real-Git runner cases, verify the four regressions fail before the change, then add the work-mode rebase helper, update the design bullet, format and run checks.

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

Planning 2026-11-18: took over giving `_agent_command` a `directory` from `TASK-373`, whose third cold read showed the runner half could not be tested there, because `_worktree` refuses a leftover rebase.

Cold read 2026-11-18 (the `directory` bullet) outcomes: accepted a `doing` case alongside the `error` case in criterion 2, so both render paths are checked; the exact rebase text and its position; the fails-before clause; keyword-only `directory`.

Planning needed: the prescribed stash identification is not safe under the concurrency it explicitly allows. If another worktree pushes a stash between the before and after lists, their set difference contains multiple IDs, not one; if an entry is dropped or shifted between finding its stash@{n} and dropping it, the wrong stash can be removed. The per-ticket run lock in src/chitty/run.py does not serialize different tickets. The ticket needs a decision on a concurrency-safe identification and drop protocol, including interaction with other Git stash users, plus a deterministic real-Git test fixture, action and assertions that exercise the interleaving and prove the correct stash is preserved or dropped. The existing fixed-case tests do not specify that test. No implementation or verification was started.

Replanned 2026-11-21: the stash concurrency blocker is settled by not using the shared stash list at all. Saved work goes to the per-ticket ref `refs/chitty/stash/<ID>` (see the Description).

Split 2026-11-21 after a cold read found it too large: `TASK-524` (save and restore helpers, no runner change) and `TASK-525` (saved work that cannot be restored). Keep this ticket in planning until `TASK-524` lands; then compare with the landed helpers, cold-read and move to `todo`.

Also waits for `TASK-534` (`restore_work`), split from `TASK-524` on 2026-11-21.

Planning needed: the specified runner tests exercise only a `doing` ticket, but the description also requires rebasing after a `todo` claim with `autocommit = false`. `tests/test_run_claims_on_branch.py` enables autocommit and does not cover saving an uncommitted claim across a rebase. The existing cases would pass if the runner skipped rebasing `todo` tickets or lost their claim. Specify the real-Git fixture, action and assertions for that case, including what setup and the agent must observe.

The prescribed non-conflict `ChittyError` path also requires restoring saved work before propagating the error, but no test describes how to trigger that failure or verify restoration and propagation. Specify a deterministic fixture, action and assertions for this path. The three existing cases cover successful rebase and conflict only; `src/chitty/git.py` shows that `rebase_onto` can raise for other failures.

I inspected the runner call site, Git helpers, and review and claim test fixtures. No implementation or regression verification was started; consequently `make check` and the requested fail-before evidence remain unchecked.

Replanned 2026-11-22: added case 4 (`todo` ticket with an existing branch) and case 5 (non-conflict failure), and dropped the untested `autocommit = false` sentence.

Work paused after inspecting the runner call site, Git helpers and review test fixture. The plan is recorded; no implementation or regression tests have been written, and fail-before evidence and make check remain outstanding.

Planning needed: the description requires the rebase before setup for every work-mode status, but cases 1, 2 and 4 only observe the branch after the run or at agent start; none observes setup. An implementation that rebases after setup would pass them while violating the requirement. Specify a real-Git setup fixture, action and assertions proving setup sees the rebased branch. The prescribed cases cover doing and todo but not error repair: an implementation that skips rebasing error tickets would also pass. Specify a fixture, action and assertions for an error ticket proving its work session rebases before setup. The existing claim tests cover todo/doing and failure, not error-mode rebase (tests/test_run_claims_on_branch.py); src/chitty/run.py selects error for repair and runs the same work setup path. The five described cases otherwise identify the relevant success, conflict, saved-work and non-conflict failure checks; git.rebase_onto, save_work and restore_work exist. No implementation or tests were written, so fail-before evidence, runtime behavior and make check could not be verified. Decide and specify the missing tests before implementation; the prescribed tests alone do not verify the stated scope and ordering.

Replanned 2026-11-22: setup now records its `git log` in case 1; the `todo` and `error` status cases moved to `TASK-545`.

Planning needed: the description requires rebasing every work-mode status, but also says this ticket is tested on doing tickets and moves the todo and error cases to TASK-545. The specified tests cannot detect skipping the rebase for todo or error, despite that being required here. src/chitty/run.py claims todo before setup and selects error for repair; tests/test_run_claims_on_branch.py does not verify rebase for either status. Decide whether to restrict this ticket's implementation requirement to doing or specify the fixtures, actions and assertions for todo and error here, including setup ordering. This is the same unresolved coverage issue identified in the previous planning note, notwithstanding the split.

I inspected the runner call site, git save/restore/rebase helpers, review fake-agent fixture, claim tests and runner plan. The described doing cases cover the other stated paths, including setup ordering and the patched non-conflict failure. No implementation or tests were written; fail-before evidence, runtime behavior and make check remain unverified.

Replanned 2026-11-22: this ticket now rebases `doing` tickets only, matching its tests; `TASK-545` extends it to `todo` and `error`.

Runner error (agent): TASK-370 was unchanged; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-370`

Split again 2026-11-22: the worker model gave up a third time (five sessions, no code). Runner wiring is `TASK-546`.

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
- 2026-11-18T18:17:17Z lively-quartz-crane: changed description
- 2026-11-18T18:19:34Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:19:34Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:19:36Z lively-quartz-crane planning → todo
- 2026-11-18T20:44:39Z lively-quartz-crane: changed description, notes
- 2026-11-18T20:44:39Z lively-quartz-crane todo → planning
- 2026-11-18T20:44:44Z lively-quartz-crane planning → cold-read
- 2026-11-18T20:46:32Z lively-quartz-crane: changed description, acceptance criteria, notes
- 2026-11-18T20:46:32Z lively-quartz-crane cold-read → planning
- 2026-11-18T20:46:37Z lively-quartz-crane planning → todo
- 2026-11-20T19:05:55Z daring-ebony-heron todo → doing
- 2026-11-20T19:07:26Z daring-ebony-heron: changed owner, notes
- 2026-11-20T19:07:26Z daring-ebony-heron doing → planning
- 2026-11-21T23:08:26Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-21T23:08:55Z lively-zinc-newt: changed description
- 2026-11-21T23:08:55Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:11:38Z lively-zinc-newt: changed dependencies, description, acceptance criteria, notes
- 2026-11-21T23:11:38Z lively-zinc-newt cold-read → planning
- 2026-11-22T00:06:48Z lively-zinc-newt: changed dependencies, notes
- 2026-11-22T01:29:17Z lively-zinc-newt: changed dependencies, description, acceptance criteria
- 2026-11-22T01:29:17Z lively-zinc-newt planning → cold-read
- 2026-11-22T01:33:50Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T01:33:50Z lively-zinc-newt cold-read → todo
- 2026-11-22T01:38:30Z youthful-zinc-jay todo → doing
- 2026-11-22T01:41:23Z youthful-zinc-jay: wrote the plan
- 2026-11-22T01:42:15Z youthful-zinc-jay: changed owner, notes
- 2026-11-22T01:42:15Z youthful-zinc-jay doing → planning
- 2026-11-22T01:42:49Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-22T01:42:49Z lively-zinc-newt planning → todo
- 2026-11-22T01:43:39Z witty-violet-badger todo → doing
- 2026-11-22T01:45:27Z witty-violet-badger: wrote the plan
- 2026-11-22T01:45:43Z witty-violet-badger: changed notes
- 2026-11-22T01:46:04Z witty-violet-badger: changed owner, notes
- 2026-11-22T01:46:04Z witty-violet-badger doing → planning
- 2026-11-22T01:47:40Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-22T01:47:40Z lively-zinc-newt planning → todo
- 2026-11-22T01:52:30Z lively-violet-quail todo → doing
- 2026-11-22T01:54:53Z lively-violet-quail: changed owner, notes
- 2026-11-22T01:54:53Z lively-violet-quail doing → planning
- 2026-11-22T01:56:07Z lively-zinc-newt: changed description, notes
- 2026-11-22T01:56:07Z lively-zinc-newt planning → todo
- 2026-11-22T01:57:19Z able-umber-dormouse todo → doing
- 2026-11-22T02:00:32Z able-umber-dormouse: changed notes
- 2026-11-22T02:00:32Z able-umber-dormouse doing → error
- 2026-11-22T02:01:58Z lively-zinc-newt: changed title, labels, description, acceptance criteria, notes
- 2026-11-22T02:01:58Z lively-zinc-newt error → todo
- 2026-11-22T02:02:30Z lively-zinc-newt todo → cold-read
- 2026-11-22T02:04:16Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T02:04:16Z lively-zinc-newt cold-read → todo
