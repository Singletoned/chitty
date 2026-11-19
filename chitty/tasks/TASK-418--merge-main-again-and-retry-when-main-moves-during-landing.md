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
- After the last attempt fails because `main` moved, raise `ChittyError` with the message `main moved during each of the 3 landing attempts` (the number from the constant). `main`, the branch and the worktree are left as they are, so a later run can retry.
- No wait between attempts: each attempt already takes as long as the check.
- Out of scope: a dirty main checkout before landing (`git.require_clean`), which is a separate ticket; making Chitty writes take the landing lock.

Tests: in a new `tests/test_landing_retry.py`, reusing the setup of `TestLanding` in `tests/test_landing.py`: write `from tests import test_landing` and subclass `test_landing.TestLanding` (importing the class itself would make unittest run all of `TestLanding` twice). Call `_land` directly with a check command `<sys.executable> <script> <main checkout> <count file> <mode>`, a Python script in the test's temporary directory (`shlex.split` splits the command, so these paths must contain no spaces). On each run the script appends a line to the count file, which lives outside the repository; after 10 runs it exits non-zero, so an unbounded retry fails instead of hanging. On the runs the mode chooses, it writes a new file named from the run count in the main checkout, then runs `git -C <main checkout> add` and `git -C <main checkout> commit`.

No property: a fixed set of four cases (moves once, moves every time, conflicts on the second merge, fast-forward fails without `main` moving), each listed and tested. Not tested: that the config and protected-file checks rerun on each attempt; a change `main` gains is merged into the branch, so those checks cannot tell a rerun from no rerun.

## Acceptance Criteria

- [ ] When the check commits to `main` on its first run only, `_land` succeeds: `main` contains both that commit and the ticket branch's commits, the count file has two lines, and the worktree and branch are removed. It fails before the change with the `--ff-only` error
- [ ] When the check commits to `main` on every run, `_land` raises `ChittyError` with `main moved during each of the 3 landing attempts`; the count file has three lines, `main` has exactly the three new commits on top of its starting point and none of the branch's, and the worktree and branch remain
- [ ] When the check's first run changes the `status:` line of the ticket file in the main checkout from `todo` to `planning` and commits it (the line `finish_ticket` changes to `done`), `_land` raises the existing conflict error, whose message contains `conflicts in`, on the second attempt; `main` holds no branch commit, and the worktree remains
- [ ] When the branch adds a file `added.txt` and the check's first run writes an untracked `added.txt` in the main checkout without committing it, `_land` raises `ChittyError` after one attempt: the count file has one line, the message does not contain `main moved`, and `main` and the worktree are unchanged. `make check` passes

## History

- 2026-11-19T12:06:28Z quick-ginger-lapwing → planning
- 2026-11-19T12:06:46Z quick-ginger-lapwing: changed acceptance criteria
- 2026-11-19T12:06:51Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T12:09:10Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T12:09:13Z quick-ginger-lapwing: changed description, acceptance criteria
