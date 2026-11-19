---
title: Merge `main` again and retry when `main` moves during landing
status: planning
priority: high
created: 2026-11-19
---

## Description

Landing (`_land_locked` in `src/chitty/run.py`) merges `main` into the ticket branch, runs `setup` and the landing check in the worktree, then runs `git merge --ff-only <branch>` in the main checkout (`git.fast_forward`). Other sessions and runners commit to `main` while the check runs, which takes minutes. When `main` gains a commit after the merge, the fast-forward fails (`Diverging branches can't be fast-forwarded`) and the run stops. Seen 2026-11-19 at 11:34 with `TASK-416`: the runner merged `main` at 11:34:29, a planning `chitty edit` committed to `main` at 11:34:43, and landing failed. The landing lock (`locks.landing_lock`) serialises runners, but ordinary Chitty writes on `main` do not take it, and should not wait minutes for a check. Inbox suggestion of 2026-11-14, "Retry landing when main moves during the landing check".

Decisions:

- Make landing an attempt loop of at most `LANDING_ATTEMPTS = 3` attempts (a module-level constant in `src/chitty/run.py`). Each attempt runs the steps from `git.merge(worktree, main_branch)` to `git.fast_forward(main_root, branch)` as today, including the conflict, config and protected-file checks, `setup` and the landing check. When `git.fast_forward` raises `ChittyError` and `git.is_ancestor(main_root, main_branch, branch)` is false (`main` moved), start the next attempt. Any other failure raises as today.
- After the last attempt fails because `main` moved, raise `ChittyError` saying `main` moved during each of the 3 landing attempts. `main`, the branch and the worktree are left as they are, so a later run can retry.
- No wait between attempts: each attempt already takes as long as the check.
- Out of scope: a dirty main checkout before landing (`git.require_clean`), which is a separate ticket; making Chitty writes take the landing lock.

Tests: in a new `tests/test_landing_retry.py`, reusing the setup of `TestLanding` in `tests/test_landing.py` (inherit it), calling `_land` directly with a check command that is a script in the test's temporary directory. The script appends a line to a count file outside the repository on each run, and, on the runs the test chooses, commits a new file (named from the run count, so each is distinct) to `main` with `git -C <main checkout> commit`. No property: a fixed set of three cases (moves once, moves every time, conflicts on the second merge), each listed and tested.

## Acceptance Criteria

- [ ] When the check commits to `main` on its first run only, `_land` succeeds: `main` contains both that commit and the ticket branch's commits, the count file has two lines, and the worktree and branch are removed. It fails before the change with the `--ff-only` error
- [ ] When the check commits to `main` on every run, `_land` raises `ChittyError` saying `main` moved during each of the 3 attempts; the count file has three lines, `main` has exactly the three new commits on top of its starting point and none of the branch's, and the worktree and branch remain
- [ ] When the check's first run commits to `main` a change to a file the branch also changed (the ticket file, which `finish_ticket` changes), `_land` raises the existing conflict error, whose message contains `conflicts in`, on the second attempt; `main` holds no branch commit, and the worktree remains. `make check` passes

## History

- 2026-11-19T12:06:28Z quick-ginger-lapwing → planning
- 2026-11-19T12:06:46Z quick-ginger-lapwing: changed acceptance criteria
