---
title: Save uncommitted worktree work under a `refs/chitty/stash` ref
status: done
parent: TASK-370
created: 2026-11-21
---

## Description

Split from `TASK-370` on 2026-11-21, and split again the same night after the worker model gave up on the whole helper pair in one session. Before rebasing a ticket worktree onto `main`, the runner must set uncommitted work aside and bring it back afterwards. The stash list (`refs/stash`) is shared by every worktree, so concurrent runs and people could pick up or drop each other's entries. This ticket adds only `save_work`, which keeps the saved work under a ref the caller names. `restore_work` is `TASK-534`; the round-trip property is `TASK-535`; `TASK-370` wires them into `chitty run`. Nothing calls `save_work` yet.

In `src/chitty/git.py`, using `_git` for commands that must succeed:

- `save_work(root: Path, ref: str, message: str) -> bool`.
- First check `ref`: it must start with `refs/chitty/stash/` and have a non-empty remainder; otherwise raise `ChittyError(f"saved work must use a ref under refs/chitty/stash/: {ref}")` before running any Git command. Put this check in a helper `_check_saved_work_ref(ref: str) -> None` so `TASK-534` can reuse it.
- If `git status --porcelain --untracked-files=all` is empty (it leaves out ignored files, and lists untracked files whatever `status.showUntrackedFiles` says), return `False` and change nothing.
- If `ref` already exists (`git rev-parse --verify --quiet <ref>` succeeds), raise `ChittyError(f"{ref} already exists; apply it with git stash apply {ref} and delete it with git update-ref -d {ref}")` and change nothing.
- Otherwise run `git add -A`, then `git stash create <message>`; if its output is empty, raise `ChittyError` naming `root` (never call `update-ref` with an empty commit); then `git update-ref <ref> <commit>`, `git reset --hard` and `git clean -fd` (which keeps ignored files). Return `True`.
- Never run `git stash push`, `pop` or `drop`, and never touch `refs/stash`.

Tests: new `tests/test_git_saved_work.py`, real Git in temporary directories (`git init -b main`, local `user.name` and `user.email`, one committed file `a.txt`), one repository per test:

- `refs/stash` (in a repository with no stash), `refs/heads/x`, `refs/chitty/stash/` and `refs/chitty/stashX/TASK-1` each raise the namespace message, and leave `git for-each-ref` output, `git stash list` and the worktree bytes unchanged.
- A clean worktree, with only an ignored file (listed in a committed `.gitignore`) changed, returns `False` and creates no ref.
- With an edit to `a.txt`, a staged new file `s.txt` an untracked file `u.txt` and an ignored file `ign.log` (listed in the committed `.gitignore`): returns `True`; `ign.log`'s bytes are unchanged; `git status --porcelain` is empty afterwards; `git show refs/chitty/stash/TASK-1:a.txt`, `:s.txt` and `:u.txt` give the edited bytes; `git stash list` is unchanged.
- With `git config status.showUntrackedFiles no` and only an untracked file `n.txt`: returns `True`, and `git show refs/chitty/stash/TASK-1:n.txt` gives its bytes.
- An existing `refs/chitty/stash/TASK-1` raises the message above and leaves the worktree bytes and the ref's commit unchanged.

No property here: the round trip is `TASK-535`. Before implementing, add `save_work` raising `NotImplementedError`, confirm the tests fail, then implement and run `make check`.

## Acceptance Criteria

- [ ] The five `save_work` tests pass, and each fails against a `NotImplementedError` stub
- [ ] `make check` passes

## Plan

Add five real-Git regression tests and a stub, verify each fails, implement save_work, then format and run checks.

## Notes

Planning blocker: the API accepts a caller-named ref without restriction, but the specified save sequence updates that ref while also promising never to touch `refs/stash`. If the caller supplies `refs/stash` in a repository with no stash, the existence check succeeds in finding no ref and `git update-ref refs/stash <commit>` creates the shared stash ref. Likewise, restore would delete an existing `refs/stash` after applying it. Decide and specify the allowed ref namespace and error behaviour, including a test for forbidden refs, or explicitly narrow the promise and caller contract. This affects the central isolation guarantee, so it is not a small implementation default.

I inspected the specified save and restore sequences, `src/chitty/git.py` and `tests/test_git.py`; the remaining examples and property describe their fixtures and assertions. I could not verify their passing or failing behaviour because no helpers or tests have been implemented. The existing plan is recorded; no implementation changes were made.

Replanned 2026-11-21: the ref namespace blocker is settled in the Description (refs outside `refs/chitty/stash/` are refused, with a test).

Work started: reviewed the ticket and existing Git helpers and tests, and recorded the approach. No implementation or regression tests have been written or verified yet.

Planning blocker: the round-trip property requires drawing 1 to 6 committed files and then a mix including a tracked file edited and left unstaged, a tracked file edited and staged, and a tracked file deleted. For a draw of one committed file, those three final states cannot all be represented: a deleted file cannot simultaneously retain an unstaged edit, and the property also requires at least one separately staged edit. Please specify whether every example must contain all three kinds of tracked change (and raise the minimum committed file count accordingly), or how the mix is to vary for small draws, including the intended assertions. Choosing either would change the requested test rather than resolve a clear omission.

I inspected the remaining examples and the existing helpers and tests; their fixtures and assertions are described. No helpers or tests were implemented, so neither the stub failures nor the passing behavior or make check were verified.

Replanned 2026-11-21: the change mix is drawn per committed file; see the Description.

Runner error (agent): TASK-524 was unchanged; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-524`

Split again 2026-11-21: the worker model returned five sessions saying it could not finish in one turn, with no code. Restore is `TASK-534`; the property is `TASK-535`.

All five regression tests failed against the NotImplementedError stub (unittest exit 1).

Reviewed:
1: pass - `make check` ran all five tests successfully; substituting a `NotImplementedError` stub at runtime ran five tests and reported eight errors, covering all five tests and four invalid-ref subtests.
2: pass - `make check` completed successfully: ruff, pyright and 1039 tests OK.

## Summary

Implemented private-ref work saving and five real Git tests. All five failed against the stub; make check passed (1039 tests).

## History

- 2026-11-21T23:10:55Z lively-zinc-newt → planning
- 2026-11-21T23:11:07Z lively-zinc-newt: changed description
- 2026-11-21T23:11:07Z lively-zinc-newt planning → cold-read
- 2026-11-21T23:12:35Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T23:12:35Z lively-zinc-newt cold-read → todo
- 2026-11-21T23:46:16Z zesty-bronze-gannet todo → doing
- 2026-11-21T23:48:13Z zesty-bronze-gannet: wrote the plan
- 2026-11-21T23:48:45Z zesty-bronze-gannet: changed owner, notes
- 2026-11-21T23:48:45Z zesty-bronze-gannet doing → planning
- 2026-11-21T23:49:45Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-21T23:49:45Z lively-zinc-newt planning → todo
- 2026-11-21T23:50:08Z quick-hazel-newt todo → doing
- 2026-11-21T23:52:30Z quick-hazel-newt: wrote the plan
- 2026-11-21T23:52:54Z quick-hazel-newt: changed notes
- 2026-11-21T23:53:33Z quick-hazel-newt: wrote the plan
- 2026-11-21T23:53:43Z quick-hazel-newt: changed owner, notes
- 2026-11-21T23:53:43Z quick-hazel-newt doing → planning
- 2026-11-21T23:58:13Z lively-zinc-newt: changed description, notes
- 2026-11-21T23:58:13Z lively-zinc-newt planning → todo
- 2026-11-22T00:01:51Z daring-lilac-urchin todo → doing
- 2026-11-22T00:04:12Z daring-lilac-urchin: wrote the plan
- 2026-11-22T00:05:10Z daring-lilac-urchin: changed notes
- 2026-11-22T00:05:10Z daring-lilac-urchin doing → error
- 2026-11-22T00:06:41Z lively-zinc-newt: changed title, description, acceptance criteria, notes
- 2026-11-22T00:06:41Z lively-zinc-newt error → cold-read
- 2026-11-22T00:07:49Z lively-zinc-newt: changed description
- 2026-11-22T00:07:49Z lively-zinc-newt cold-read → todo
- 2026-11-22T00:16:51Z tidy-khaki-raven todo → doing
- 2026-11-22T00:18:07Z tidy-khaki-raven: wrote the plan
- 2026-11-22T00:18:36Z tidy-khaki-raven: changed notes
- 2026-11-22T00:20:03Z tidy-khaki-raven: changed summary
- 2026-11-22T00:20:04Z tidy-khaki-raven doing → review
- 2026-11-22T00:25:14Z witty-fawn-gannet: changed notes
- 2026-11-22T00:25:14Z witty-fawn-gannet review → done
