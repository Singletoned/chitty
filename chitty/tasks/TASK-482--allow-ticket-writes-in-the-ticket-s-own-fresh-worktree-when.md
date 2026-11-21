---
title: Allow ticket writes in the ticket's own fresh worktree when `main` holds its copy
status: doing
parent: TASK-376
created: 2026-11-21
---

## Description

Split out of `TASK-378` on 2026-11-21, when its worker found the whole read switch too large for one session. After `TASK-378`, a ticket in a fresh ticket worktree (its branch `task-6` made at `main`'s tip, with no commit of its own yet) is read from `main`, because `main`'s copy is authoritative until the branch changes it. `Repo._require_current_version` (`src/chitty/store.py`) refuses a write when `stored.branch` is neither `None` nor the current branch, so the first write in such a worktree, including the runner's claim on the branch (`TASK-384`), would be refused. This ticket adds the allowance first. Under today's reads it only adds a case where a write is allowed, so nothing that works today stops working.

Decision (owner, 2026-11-20): `_require_current_version` also returns without raising when all of these hold: the current branch is the ticket's own branch (`str(stored.id).lower()`, so `task-6` for `TASK-6`); `stored.branch` is the configured main branch; and `git.changed_since_split(self.root, f"refs/heads/{main}", f"refs/heads/{own}", paths)` (`src/chitty/git.py`) is false, where `paths` is the union of the paths (the first element of each `(path, content)` pair) returned by `self._ref_ticket_files(ref, stored.id)` for those two refs; `<main>` is `self._main_branch()`. The write then commits on the branch, which puts the branch ahead of `main`, so every checkout reads the ticket from the branch afterwards. A branch merged into `main` that `main` has changed since is still refused. Every other case is refused as today; `TASK-385` replaces the guard later.

Tests: real Git, in a new `tests/test_own_worktree_writes.py` with a class inheriting `CliTestCase` from `tests/test_cli.py`, set up with `git init -b main` and `autocommit = true` as `tests/test_check_cross_branch_references.py` does. The linked worktree is made with `git worktree add -b task-6 <dir> main` after `TASK-6` is committed on `main`; the CLI runs with that directory as the working directory. The direct tests open `Repo.open(<worktree>)` and build the `StoredTask` with the given `branch` and the ticket's real path and parsed task (read from the file). `main` gets its post-split commit from the main checkout, which stays on `main`; the merge is `git merge --ff-only task-6` run in the main checkout. The `feature` checkout is another linked worktree, `git worktree add -b feature <dir> main`. The failing CLI case passes `exit_code=1` to `run_cli`. Alphanumeric ticket IDs are out of scope here; the rule only lower-cases `str(stored.id)`. No property: a fixed set of branch relations, each in the criteria.

## Acceptance Criteria

- [ ] In the linked worktree of a fresh `task-6` made at `main`'s tip, `chitty edit TASK-6 --note x` succeeds and commits on `task-6`; after `task-6` is fast-forward merged into `main` and a further `main` commit changes `TASK-6`, the same edit in that worktree exits 1 with the `_require_current_version` message naming `main` and makes no commit (guards that pass before the change too: under today's history-based reads the ticket is not read from `main` here; they protect `TASK-378`, which switches the reads)
- [ ] Direct tests of `Repo._require_current_version` with a `StoredTask` whose `branch` is `main`, from a checkout on branch `task-6`: it returns when `main` has not changed `TASK-6`'s files since `task-6` split from it (only `main`'s side matters: had the branch changed them, the ticket would be read from `task-6`, which is allowed today); it raises when `main` changed them since the split; it raises with `stored.branch` set to `feature` from `task-6` while `TASK-6` is unchanged; it raises from a checkout on branch `feature` (each against a real Git repository; the unchanged-`main` case fails before the change, which is this ticket's fails-before evidence)
- [ ] `make check` passes

## Plan

Add real-Git linked-worktree regression tests for CLI writes and direct guard branch relationships, confirm the new allowances fail before the fix, then implement the specified main-side path comparison and run the full checks.

## Notes

Criterion 1 says the first fresh-worktree CLI edit fails before this change, but the specified real-Git test passes both before and after the main-side change without any implementation fix. Current single-ticket reads still use the old history-based lookup; TASK-378, which depends on this ticket, switches them to source_copy. Therefore the CLI regression cannot prove this guard change before TASK-378, and the criterion's required pre-fix failure is currently impossible. Planning needs to decide how to split or revise the CLI regression and its evidence without introducing a dependency cycle. The direct unchanged-main guard test does fail before the fix with the expected branch-main error; the other direct guard cases pass. Partial tests are committed in cf35be2f, with the direct regression intentionally failing. make check passed formatting, lint and pyright but timed out after 120 seconds during unittest; the targeted unittest run confirms one error and four passes. No implementation fix was made.

Criterion 1 requires a pre-fix CLI failure that cannot occur until dependent TASK-378 changes the read path; see the preceding note for evidence and the planning decision needed.

Planning 2026-11-21: criterion 1 restored as guards (an earlier planning edit wrongly said the CLI case fails today); criterion 2's direct unchanged-`main` test is the fails-before evidence, as this worker found. Resumed as `doing` with the partial tests in `cf35be2f`.

Check failed before this session: check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
691 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 898 test suites (898 total tests) across 16 workers
................................................................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxqccl0n0/repo/chitty/tasks/TASK-1--one.md actor test-agent
.....................━━━━ chitty run · 01:34:15 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
................................................................./Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
.............E.................................................................................................................................................kill: 68620: No such process
...........kill: 71746: No such process
....................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
............./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/CLAUDE.md
.........Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpb0mjpild/repo/.worktrees/task-1...
.Check passed; work agent is working on TASK-1...
......TASK-1: doing → review
..no next ticket for --mode work
......../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbqrnbe27/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp69ivbi6r/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp0tvcpu9w/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8m4bxz1m/repo/CLAUDE.md
.../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpif33ymgp/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgqtijzjt/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv00u4hpp/repo/CLAUDE.md
....................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
..............................landed TASK-1
landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_guard_allows_unchanged_main (tests.test_own_worktree_writes.TestOwnWorktreeWrites.test_guard_allows_unchanged_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-482/tests/test_own_worktree_writes.py", line 57, in test_guard_allows_unchanged_main
    Repo.open(self.worktree)._require_current_version(self.stored(self.worktree, "main"))
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-482/src/chitty/store.py", line 1209, in _require_current_version
    raise ChittyError(
        f"{stored.id}'s latest committed version is on branch {branch}; {instruction}"
    )
chitty.errors.ChittyError: TASK-6's latest committed version is on branch main; run Chitty in worktree /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgj78fn7a/repo

----------------------------------------------------------------------
Ran 898 tests in 130.455s

FAILED (errors=1)
make: *** [check] Error 1

```

## History

- 2026-11-21T01:20:56Z quick-pearl-lapwing → planning
- 2026-11-21T01:23:37Z quick-pearl-lapwing planning → cold-read
- 2026-11-21T01:24:40Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-21T01:24:40Z quick-pearl-lapwing cold-read → todo
- 2026-11-21T01:25:07Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-21T01:25:34Z intrepid-yellow-heron todo → doing
- 2026-11-21T01:28:49Z intrepid-yellow-heron: wrote the plan
- 2026-11-21T01:32:17Z intrepid-yellow-heron: changed notes
- 2026-11-21T01:32:30Z intrepid-yellow-heron: changed owner, notes
- 2026-11-21T01:32:30Z intrepid-yellow-heron doing → planning
- 2026-11-21T01:33:32Z quick-pearl-lapwing: changed acceptance criteria, notes
- 2026-11-21T01:33:32Z quick-pearl-lapwing planning → doing
- 2026-11-21T01:36:01Z youthful-violet-wren: changed notes
