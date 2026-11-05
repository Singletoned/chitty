---
title: Have cold reads implement tickets in a detached worktree
status: todo
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

A cold read that only reads the ticket and code has to imagine what happens when someone follows it. In `echonomicon`, about 15 tickets planned for a weaker model showed that implementing the ticket finds faults a read-only pass misses: a test that would have read the real user library, a test that passes with or without the fix, and a criterion that a wrong fix (`== 500` for `>= 400`) would still satisfy. The human decided on 2026-11-05 that a read of a ticket that changes code should implement it on a cheap model, which is the point of the exercise, and that a reasoning read belongs with a stronger model. It should use a throwaway worktree rather than a clone, so the Git history can be kept.

A deleted branch is not a good way to keep it. A test on 2026-11-05 showed that after `git worktree remove` and `git branch -D` no reflog names the commit, only `git fsck --unreachable` finds it, as a bare hash, and it can be pruned after two weeks. A named ref avoids this. A detached worktree also creates no branch, which matters because `git.py` treats ticket copies on `refs/heads` and `refs/remotes` as candidates for the newest copy, and `TASK-177` will count their numbers.

In `src/chitty/roles/plan.md`, replace the first sentence of the bullet starting "Cold-read every ticket", which holds the list of what to report, with this wording, adjusting only line wrapping. Keep the rest of the bullet, on recording outcomes and splitting:

"Cold-read every ticket, even a small one. If it changes code, a fresh agent on a cheap model, close to the one that will do the work, implements it from the ticket alone in a throwaway worktree, and runs its tests with and without the fix. If there is nothing to run, a stronger model reads the ticket and referenced code instead. Either way, the reader reports done meaning, likely files, open decisions, unverified behaviour, unhandled states, and wrong claims."

Add a new bullet after the whole of that bullet, so that its text on recording outcomes stays with it:

"Start an implementing read with `git worktree add --detach .worktrees/read-<ID>` and the repository's setup command, not on a branch, because Chitty reads tickets from every branch. Run the reader with `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` unset, or a shared install ends up pointing at a worktree about to be deleted. The reader runs no Chitty writes and leaves `chitty/` unchanged. It commits its own work, keeps it with `git update-ref refs/cold-read/<ID>/<n> HEAD`, where `<n>` is the next number free for that ticket, starting at 1, then runs `git worktree remove --force .worktrees/read-<ID>`. `git for-each-ref refs/cold-read` lists kept reads."

Replace the "Cold read:" paragraph's description in `PLAN.md` so it agrees, recording the decision and date and why a ref rather than a branch. This file ships to every repository, so do not name `make` or a particular model. `src/chitty/roles/plan.md` does not reach `AGENTS.md`, so no `chitty init` or version bump is needed. `TASK-188` adds bullets to the same file and sets a limit of about 35 lines: that limit may grow to about 45 for this, and whichever lands second merges the wording.

Out of scope: tooling that runs reads, which `TASK-125` holds, and deleting old refs.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py`, collapsing whitespace in `guide("plan")` first so that line wrapping cannot break it, shows it containing `implements it from the ticket alone`, `with and without the fix`, `Either way, the reader reports done meaning`, `git worktree add --detach`, `UV_PROJECT_ENVIRONMENT`, `git update-ref refs/cold-read/<ID>/<n> HEAD` and `git worktree remove --force`, and fails against the current `plan.md`
- [ ] `PLAN.md`'s cold read paragraph describes implementing reads and reasoning reads, gives the decision's date, and says why the work is kept under a ref

## Notes

Suggestion origin: echonomicon

Refitted on 2026-11-05 with the human. The suggestion's other two parts, repeating reads and comparing decisions with criteria, are now a separate ticket. Its use of `git clone` is replaced by a detached worktree, which also has a real `.git`, so the `git archive` false failure it warned of does not apply.

Implementing cold read by a fresh Haiku subagent, 2026-11-05, the first using this method, kept at `refs/cold-read/TASK-194/1`. All commands in the method worked as written: the detached worktree, setup, `make check`, `update-ref`, `for-each-ref`, and the commit on no branch. Fixed: replacing the first sentence would have lost the list inside it; a test on exact phrases broke on line wrapping in my own wording; how `<n>` is chosen; where the bullet goes; and the criterion now covers the keeping and removal steps. Rejected: testing `PLAN.md`'s paragraph, which is prose for the reviewer to read; an 82-column line, since the limit applies to commands shown to people; and telling readers to use `uv run chitty`, because only this repository has a global `chitty` older than its checkout, and `plan.md` ships to all. Not repeated: nothing found was a fault of the design, and `TASK-195` is not yet decided.

Found after the read, 2026-11-05, and serious: the three trial reads broke the global `chitty`. They inherited `UV_PROJECT_ENVIRONMENT=~/.envs/chitty` from the planning session, and a bare `uv run` in a worktree repointed that editable install there; `make` is safe because the `Makefile` sets both variables. Removing the worktree then left `ModuleNotFoundError: No module named 'chitty'`. `uv sync --all-extras` in the main checkout restored it. The method now unsets them.

Second implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-194/2`. Fixed: where the new bullet goes, since "straight after it" could split the bullet; "commits nothing under `chitty/`" beside "commits its work"; and the `PLAN.md` criterion now requires the date and the reason. Rejected: checking the order of the commands in the test, because the wording is given whole. It found no contradiction between description and criteria. Another read follows, since these came back with changes.

Third implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-194/3`: nothing serious. The test failed on all seven phrases without the change and passed with it, and `make check` exited 0. Rejected: testing `PLAN.md` and the removal of the old sentence, because the wording is given whole and a reviewer can compare it; a ticket that changes only Markdown and adds a test, which has something to run, so it is implemented; naming `uv` tools in a shared file, because the two variable names are what prevents the fault and do nothing elsewhere; a command wrapped inside backticks, which a worker can avoid when wrapping; and how to find `<n>`, because the same bullet gives `git for-each-ref refs/cold-read`.

## History

- 2026-11-05T17:52:45Z mellow-newt → backlog
- 2026-11-05T17:52:46Z mellow-newt: changed notes
- 2026-11-05T17:53:53Z mellow-newt: changed title, priority, parent, description, acceptance criteria, notes
- 2026-11-05T17:59:25Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T17:59:26Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T17:59:27Z mellow-newt backlog → todo
- 2026-11-05T18:06:36Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:08:05Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:13:36Z mellow-newt todo → backlog
- 2026-11-05T18:19:21Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:19:22Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:31:22Z mellow-newt: changed notes
- 2026-11-05T18:31:23Z mellow-newt backlog → todo
