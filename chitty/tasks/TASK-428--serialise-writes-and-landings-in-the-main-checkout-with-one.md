---
title: Serialise writes and landings in the main checkout with one short lock
status: error
priority: high
created: 2026-11-19
---

## Description

Two runners, or a runner and a planner, change the main checkout at the same time without coordinating. Every Chitty write there (a runner's claim, `chitty add`, `chitty edit`, and the setup upgrade) writes files and then commits them, holding no lock. Landing (`_land_locked` in `src/chitty/run.py`) checks that the main checkout is clean (`git.require_clean`) once at the start, then spends about a minute on `setup` and the landing check before `git.fast_forward`. So a write that starts during a landing leaves the main checkout briefly dirty and the landing fails (`TASK-410`'s dirty-tree error, 2026-11-19), or the fast-forward refuses to overwrite a file the write changed, and two writes at once can collide on Git's `index.lock`. Decided with the owner 2026-11-19: serialise these with one short lock. This replaces `TASK-419`.

Decisions:

- New lock in `src/chitty/locks.py`: `MAIN_CHECKOUT_LOCK = "main-checkout.lock"`, in the same directory as the other locks (`_directory(root)`, which is `<git common dir>/chitty/run`), and a context manager `main_checkout_lock(root: Path)` built like `landing_lock`: a blocking exclusive `flock` that the kernel releases if the process dies. When `_directory(root)` is `None` (no Git repository), it yields without locking. It is not reentrant; no write nests inside another (checked 2026-11-19 by reading every `with self._all_or_nothing():` block in `store.py` and the private helpers they call, `_set_archived`, `_delete_done` and `_archive`: none calls another write).
- `Repo._all_or_nothing` in `src/chitty/store.py` holds `main_checkout_lock(self.root)` for its whole body when `self.root` is in a Git repository and is not a linked worktree (`git.is_linked_worktree`). Writes in a ticket worktree take no lock: each worktree has its own working tree, and its ticket has a run lock.
- `Repo._prepare_write` holds the same lock around `init_repo` and the setup commit, and `Repo.refresh_setup` holds it from its `git.dirty_paths` check through the setup commit, when they reach them in the main checkout. Accepted untested: these paths run only when the recorded `chitty_version` differs from the running one, and they use the same lock as `_all_or_nothing`, which the tests cover.
- Landing keeps `landing_lock` around the whole landing, as today, and takes `main_checkout_lock` only for the moments it touches the main checkout: around the first `git.require_clean(main_root)`, and around a new `git.require_clean(main_root)` followed by `git.fast_forward(main_root, branch)` on each attempt. It never holds `main_checkout_lock` during `setup`, the landing check or the rebase, so a write waits only seconds, never for a whole landing. Lock order is always `landing_lock` then `main_checkout_lock`; writes take only the second, so they cannot deadlock with a landing.
- `locks.locked_ids` lists every held `*.lock` in that directory as an ID, so it will list `main-checkout` while it is held, as it already lists `landing`. Accepted: no ticket has those IDs.
- Out of scope: lost updates when two processes edit the same ticket (run locks keep runners off each other's tickets), and Git commands a person runs by hand.
- Docs: in `docs/plan/next-action-and-runner.md`, add one bullet near the landing bullets describing the lock and the lock order as above.

Tests, new file `tests/test_main_checkout_lock.py`. Both use a holder: a Python script run with `subprocess.Popen([sys.executable, holder, lock_path, held, release])` that creates the lock's directory, opens `lock_path` (`<git common dir>/chitty/run/main-checkout.lock`; in these tests the root is the main checkout, so it is `<root>/.git/chitty/run/main-checkout.lock`, written out, not imported from `chitty.locks`, so the test also runs against the old code), takes `fcntl.flock(fd, fcntl.LOCK_EX)`, writes `held`, then waits (polling every 0.05 s, at most 30 s) until `release` exists, and exits. No property: the behaviour is the ordering of two real processes.

- `test_a_write_in_the_main_checkout_waits_for_the_lock`: a `CliTestCase` repository with Git (`git init -b main`, user name and email set), `autocommit = true` and one committed ticket `TASK-1`. Start the holder and wait for `held`. Start `subprocess.Popen([sys.executable, "-c", "from chitty.cli import main; main()", "edit", "TASK-1", "--note", "waited"], cwd=self.root)`. After 2 s, assert it is still running (`poll()` is `None`) and `git log -1 --format=%s` is unchanged. Create `release`; the edit exits 0 within 30 s and `git log -1 --format=%s` starts with `chitty: edit TASK-1`.
- In `tests/test_review_merge.py`: give the landing-check script in `setUp` a third argument by appending ` {self.logs / "hold_main"}` to the `check = "..."` string that `setUp` builds (after the `fail_landing_check` argument). Inside its existing `if Path('main-late.txt').exists() or Path('review-marker').exists():` block, first, when `Path(sys.argv[3]).exists()`: start, detached, a second holder script whose arguments are the main root (read from `sys.argv[3]`) and the `held` path `Path(sys.argv[3]).with_name("hold_main_held")` (that is, `self.logs / "hold_main_held"`). It takes the same lock (`<root>/.git/chitty/run/main-checkout.lock`), writes `dirty\n` to `<root>/shared.txt`, writes `held`, sleeps 2 s, runs `git -C <root> checkout -- shared.txt`, and exits, which releases the lock. Before starting it, the check script deletes `held` if it exists (the landing may retry and run the check again), and afterwards waits for `held` at most 30 s, exiting non-zero if it never appears, so an implementation that holds the lock during the landing check fails the test instead of hanging it. New test `test_landing_waits_for_a_write_in_the_main_checkout`: `self.branch_for_review(shared="branch\n")`, write `str(self.root)` to `self.logs / "advance_main"` and to `self.logs / "hold_main"`, run `self.run_cli("run", "--mode", "review")`; it lands: the output contains `landed TASK-1`, `git show main:shared.txt` is `branch\n`, and `git status --porcelain` in the main checkout is empty. On the old code the fast-forward runs while `shared.txt` is dirty and fails, so the run prints `done → error` and still exits 0 (as in `test_failing_check_after_main_advances_preserves_main_and_worktree`); the test fails at the `landed TASK-1` assertion.
- Guard, `test_a_write_in_a_ticket_worktree_does_not_wait`: in the same kind of repository, add a linked worktree with `git worktree add -b task-1 .worktrees/task-1`. With the holder holding the lock, `subprocess.run([sys.executable, "-c", "from chitty.cli import main; main()", "edit", "TASK-1", "--note", "no wait"], cwd=<worktree>, timeout=10)` exits 0 and `git -C <worktree> log -1 --format=%s` starts with `chitty: edit TASK-1`. It passes before the change too; it stops a worker locking every write.

## Acceptance Criteria

- [x] The two lock tests pass; each fails against `main` before this change, the first because the edit finishes while the lock is held, the second because the ticket goes to `error` (recorded in the notes); the worktree guard passes before and after
- [ ] The existing landing tests in `tests/test_review_merge.py` and `tests/test_landing.py` still pass; `make check` passes

## Plan

Add a blocking main-checkout flock in locks.py. Hold it across repository all-or-nothing writes and setup upgrades only in the primary checkout; linked worktrees remain unlocked. During landing, acquire it only around the initial clean-tree check and around each final clean-tree check plus fast-forward, preserving landing-lock-first ordering. Add process-level regression tests for blocked main writes, landing/write coordination, and the linked-worktree guard; document the locking model. First add and run regressions against the current implementation, then implement, format, and run make check.

## Notes

Cold read 2026-11-19 (first use of the `cold-reader` agent) outcomes: the check script waits for `held` at most 30 s, so a wrong lock fails rather than hangs; it deletes a stale `held` before each attempt; a guard that ticket-worktree writes do not wait; no locking outside a Git repository; the lock path named by the common Git directory; the no-nesting claim re-checked by the planner, including the private helpers.

Second cold read 2026-11-19 outcomes: the setup-upgrade paths are accepted untested (same lock, rare path); the `refresh_setup` dirty check is inside the lock; exact edit to the `check` string and the `held` path; the old code fails at the `landed TASK-1` assertion, since a failed landing exits 0.

Regression evidence: the main-write test failed when _all_or_nothing stopped acquiring the new lock (edit exited while holder owned it). The landing/write race test failed when the final landing lock window was removed (review moved to error). Both pass with the implementation. make check passes format, Ruff and Pyright but unittest-parallel repeatedly stalls around the same point and timed out after 3600 seconds; focused lock, review-merge and landing suites pass (43 tests).

Runner error (check): check exited with status -15:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
617 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 768 test suites (768 total tests) across 16 workers
.............................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpeqlfl7ie/repo/chitty/tasks/TASK-1--one.md actor test-agent
..................━━━━ chitty run · 20:40:37 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
...................................................................................................................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
............../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/.worktrees/task-1...
..TASK-1: doing → review
....no next ticket for --mode work
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/CLAUDE.md
...............................................chitty 0.1.31 is out: run uv tool upgrade chitty
............................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/multiprocessing/resource_tracker.py:400: UserWarning: resource_tracker: There appear to be 11 leaked semaphore objects to clean up at shutdown: {'/mp-qz9fv1be', '/mp-9dmde3pq', '/mp-f_xwkxr0', '/mp-bvmr0f_7', '/mp-bdctt16s', '/mp-9wh65ojr', '/mp-6_nj26tn', '/mp-nnv5bv40', '/mp-_3hcfa7v', '/mp-pmkx8qrc', '/mp-1qivvs5g'}
  warnings.warn(
make: *** [check] Error 143

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-428`

Error output:
````text
check exited with status -15:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
617 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 768 test suites (768 total tests) across 16 workers
.............................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpeqlfl7ie/repo/chitty/tasks/TASK-1--one.md actor test-agent
..................━━━━ chitty run · 20:40:37 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
...................................................................................................................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
............../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxm3leuqc/repo/.worktrees/task-1...
..TASK-1: doing → review
....no next ticket for --mode work
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplmalvdx_/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpg7t39m6s/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpucv0r21o/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp46rryo6h/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmd4zm246/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkuek_t0e/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6rb7ppcm/repo/CLAUDE.md
...............................................chitty 0.1.31 is out: run uv tool upgrade chitty
............................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/multiprocessing/resource_tracker.py:400: UserWarning: resource_tracker: There appear to be 11 leaked semaphore objects to clean up at shutdown: {'/mp-qz9fv1be', '/mp-9dmde3pq', '/mp-f_xwkxr0', '/mp-bvmr0f_7', '/mp-bdctt16s', '/mp-9wh65ojr', '/mp-6_nj26tn', '/mp-nnv5bv40', '/mp-_3hcfa7v', '/mp-pmkx8qrc', '/mp-1qivvs5g'}
  warnings.warn(
make: *** [check] Error 143

```
````

## Summary

Implemented the main-checkout lock and process-level tests for serialized main writes, landing/write coordination, and the linked-worktree guard. Verification: focused suites pass (43 tests); format, Ruff, Pyright pass. Follow-up: full make check remains unverified because unittest-parallel stalls and exceeded 3600 seconds.

## History

- 2026-11-19T17:48:46Z quick-ginger-lapwing → planning
- 2026-11-19T17:49:20Z quick-ginger-lapwing: changed description
- 2026-11-19T17:51:06Z quick-ginger-lapwing: changed description, acceptance criteria, notes
- 2026-11-19T17:52:42Z quick-ginger-lapwing: changed owner, description, notes
- 2026-11-19T17:52:42Z quick-ginger-lapwing planning → todo
- 2026-11-19T17:59:10Z daring-lilac-vole todo → doing
- 2026-11-19T18:01:02Z daring-lilac-vole: wrote the plan
- 2026-11-19T20:04:12Z daring-lilac-vole: changed notes, summary; ticked acceptance criteria
- 2026-11-19T20:04:12Z daring-lilac-vole doing → review
- 2026-11-19T20:59:03Z golden-coral-badger: changed notes
- 2026-11-19T20:59:03Z golden-coral-badger review → error
