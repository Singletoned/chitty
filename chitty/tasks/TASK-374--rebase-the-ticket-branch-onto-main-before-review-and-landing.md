---
title: Rebase the ticket branch onto `main` before review and landing
status: doing
labels:
  - bug
  - needs-minor
priority: high
depends_on:
  - TASK-382
  - TASK-383
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model a ticket file changes only on its branch, so ticket files rebase like any other file; there is no ticket merge (`TASK-359` is archived). Any conflict, ticket file or not, goes to an agent.

Today `_prepare_review` merges `main` into the ticket branch with `git.merge_main`, and `_land` merges it again with `git.merge` before fast-forwarding `main` (`src/chitty/run.py`), leaving merge commits on the branch and in `main`.

Decisions:

Starts after `TASK-382` and `TASK-383` land, which stop the runner writing tickets with a branch on `main`; until then a ticket file can change on both sides and conflict.

- New `git.rebase_onto(root: Path, main_branch: str) -> list[str]` in `src/chitty/git.py`: runs `git -c rerere.enabled=false rebase <main_branch>`, without `--autostash` (review and landing already refuse a dirty worktree; `TASK-370` stashes explicitly). Exit 0: return `[]`. Non-zero with a rebase still in progress and unmerged paths (`git diff --name-only --diff-filter=U`): leave it stopped and return those paths. Non-zero with a rebase in progress but no unmerged paths: run `git rebase --abort` and raise `ChittyError` with Git's output. Non-zero with no rebase in progress: raise `ChittyError` with Git's output. `TASK-370` reuses it.
- `_prepare_review` calls it instead of `merge_main`. On conflicts it runs `git rebase --abort` and fails the review as `Review failed (integration): rebasing onto <main> conflicts in <paths>` with each path in backticks, as today's merge failure does. `TASK-375` later replaces the abort with a resolution session.
- `_land` calls it instead of `git.merge`, then fast-forwards `main`. A conflict aborts the rebase and is a landing error, as today.
- Remove `git.merge` and `git.merge_main` once nothing uses them.
- Ctrl-C during either rebase aborts it and raises `RunInterrupted("rebase")` (exit 130): `_prepare_review` adapts its `KeyboardInterrupt` handler, and `_land` gains one. Retarget the two existing tests that patch `chitty.git.merge_main` to raise `KeyboardInterrupt` (`tests/test_review_merge.py` `test_interrupting_the_merge_aborts_it_and_exits_130` and the one in `tests/test_run_lock.py`) to `chitty.git.rebase_onto`, keeping their exit-130 and abort assertions, with `interrupted during rebase`.
- Existing assertions that a review leaves one merge commit (`tests/test_review_merge.py` around lines 287 and 328, `rev-list --merges --count`) now expect `0`.
- The uncommitted-files block before a review stays.
- In `docs/plan/next-action-and-runner.md`, add the principle paragraph, and say under `## Before a review` and `## Landing` that the branch is rebased onto `main`.

Tests: real-Git, fake-agent runner tests in `tests/test_review_merge.py` and `tests/test_landing.py`, with `git init -b main`; the fake reviewer writes a marker file when it starts. No property: real Git and runner processes over the fixed cases in the criteria; `rebase_onto`'s two outcomes are tested directly in `tests/test_git.py`.

## Acceptance Criteria

- [ ] `git.rebase_onto` returns `[]` and leaves no rebase in progress for a clean rebase, and returns the unmerged paths with the rebase stopped for a conflict, in `tests/test_git.py`
- [ ] A review run where `main` has a new commit to a file the branch does not touch: `git rev-list --merges main..task-<n>` is empty, `main` is an ancestor of the branch, and the fake reviewer starts once; this fails before the change
- [ ] A review run whose rebase conflicts on a code file: no rebase is in progress afterwards, the ticket is `doing` with a note containing `Review failed (integration): rebasing onto `main` conflicts in` and the path in backticks, and no reviewer starts; this fails before the change (today's note says `merging`)
- [x] A landing after a non-conflicting commit on `main` fast-forwards `main` to the rebased branch with no merge commit (`git rev-list --merges` is empty for the landed range); this fails before the change
- [x] `git.merge` and `git.merge_main` are gone, the retargeted interrupt tests and the flipped merge-count assertions pass, and `docs/plan/next-action-and-runner.md` has the principle and the rebase under both headings; `make check` passes

## Plan

Fix conflict path parsing by reading Git’s NUL-delimited unmerged path output, and add a real-Git filename-with-spaces test. Strengthen the review integration tests to assert no merge commits in main..task-1 and exactly one reviewer start, and to assert the conflict leaves no rebase in progress. Run the targeted tests against the current implementation first to confirm each regression, then implement and verify; format, run make check, and commit with Task: TASK-374.

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

Implemented `git.rebase_onto`; review and landing now rebase onto main, abort conflicts, and translate Ctrl-C to `RunInterrupted("rebase")`. Removed merge helpers. Added direct clean/conflict Git tests; updated real runner, retry, and guide coverage. Focused suites passed (72 tests). `make check` passed all 736 tests; first full run had one transient existing `tests.test_next.TestNext.test_run_cases` failure, and rerun passed. `git diff --check` passed. `chitty fix` completed with existing warnings in unrelated task files.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 744 test suites (744 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 14:30:29 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
...........................................................................................F............................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/CLAUDE.md
.......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/.worktrees/task-1...
..TASK-1: doing → review
.no next ticket for --mode work
......./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/CLAUDE.md
...............................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_run_cases (tests.test_next.TestNext.test_run_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-374/tests/test_next.py", line 1836, in test_run_cases
    no_next = self.run_cli("run", exit_code=3)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-374/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : TASK-1: blocked → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp2bw5fj54/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 744 tests in 36.057s

FAILED (failures=1)
make: *** [check] Error 1

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-374`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 744 test suites (744 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 14:30:29 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
...........................................................................................F............................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/CLAUDE.md
.......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd940zmb5/repo/.worktrees/task-1...
..TASK-1: doing → review
.no next ticket for --mode work
......./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkpz8xu6v/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpdafm5l6f/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8dzupf1l/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6g1tfifr/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpnbzhembc/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvedem84k/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp9nv8iof5/repo/CLAUDE.md
...............................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_run_cases (tests.test_next.TestNext.test_run_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-374/tests/test_next.py", line 1836, in test_run_cases
    no_next = self.run_cli("run", exit_code=3)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-374/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : TASK-1: blocked → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp2bw5fj54/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 744 tests in 36.057s

FAILED (failures=1)
make: *** [check] Error 1

```
````

Reset 2026-11-19: the runner error came from the flaky `tests.test_next.TestNext.test_run_cases`, fixed on `main` in `fe1ef0cd`; back to `review`.

Review failed (tests): New findings; no earlier review failure note exists. Fix the conflict path parsing and add the missing review regressions.
1: fail - The two tests passed in `python -m unittest tests.test_git.TestRebaseOnto` and fail with `rebase_onto` replaced by None, but a real Git conflict on `shared file.txt` returned `["shared", "file.txt"]` in a throwaway test using `TestRebaseOnto`; return complete paths and test whitespace.
2: fail - `test_agent_and_setup_see_the_branch_merged_with_main` checks ancestry but only counts merges after landing and uses an overwriting marker, not reviewer start count. Add a review-stage assertion of no merges in `main..task-1` and exactly one reviewer start; demonstrate failure on the old merge behavior.
3: fail - `test_conflict_moves_the_ticket_to_doing_without_starting_the_agent` passed in the focused unittest run, but `assert_no_merge_in_progress` checks `MERGE_HEAD`, not rebase state. Assert no rebase in progress and demonstrate the regression fails before the change. The whitespace conflict in criterion 1 also produces incorrect path names in the review note.
4: pass - `test_main_advances_during_review_and_landing_checks_merged_branch` passed; replacing `rebase_onto` with the old merge behavior made it fail with `1 != 0` merge commits.
5: pass - `make check` printed `Ran 744 tests` and `OK`; the diff removes both merge helpers, retargets interrupts and merge-count assertions, and updates both design headings.

Review follow-up: confirmed the whitespace regression before fixing it: the real-Git test returned ["shared", "file.txt"] instead of ["shared file.txt"]. NUL-delimited conflict paths now preserve filenames. The review fake-agent records merge count at startup; the regression asserts exactly one startup with zero merges. Conflict coverage also directly checks rebase_in_progress is false afterwards.

## Summary

Replaced runner merge integration with rebasing in review and landing; removed obsolete merge helpers. Updated runner guide and real-Git regression tests. Verification: focused tests (72), `make check` (736 tests), `git diff --check`, and `chitty fix`. Implementation commit: 706614ca (Task: TASK-374). No follow-ups.

## History

- 2026-11-18T09:51:20Z witty-ginger-falcon → planning
- 2026-11-18T09:52:34Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:01Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:56:03Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:56:05Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:46Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:46Z witty-ginger-falcon todo → planning
- 2026-11-18T17:57:37Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:57:39Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T17:57:41Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T18:00:09Z lively-quartz-crane planning → cold-read
- 2026-11-18T18:02:09Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:02:09Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:02:11Z lively-quartz-crane planning → todo
- 2026-11-18T18:17:15Z lively-quartz-crane: changed description
- 2026-11-19T14:20:48Z sunny-bronze-ibis todo → doing
- 2026-11-19T14:21:56Z sunny-bronze-ibis: wrote the plan
- 2026-11-19T14:29:41Z sunny-bronze-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-19T14:29:41Z sunny-bronze-ibis doing → review
- 2026-11-19T14:30:59Z sunny-indigo-vole: changed notes
- 2026-11-19T14:30:59Z sunny-indigo-vole review → error
- 2026-11-19T16:01:48Z quick-ginger-lapwing: changed notes
- 2026-11-19T16:01:48Z quick-ginger-lapwing error → review
- 2026-11-19T16:05:37Z vivid-zinc-heron: changed acceptance criteria, notes
- 2026-11-19T16:05:37Z vivid-zinc-heron review → doing
- 2026-11-19T16:08:32Z brisk-yellow-toad: wrote the plan
- 2026-11-19T16:12:55Z brisk-yellow-toad: changed notes
