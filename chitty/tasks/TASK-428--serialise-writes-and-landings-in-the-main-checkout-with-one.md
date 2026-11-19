---
title: Serialise writes and landings in the main checkout with one short lock
status: planning
priority: high
owner: planner
created: 2026-11-19
---

## Description

Two runners, or a runner and a planner, change the main checkout at the same time without coordinating. Every Chitty write there (a runner's claim, `chitty add`, `chitty edit`, and the setup upgrade) writes files and then commits them, holding no lock. Landing (`_land_locked` in `src/chitty/run.py`) checks that the main checkout is clean (`git.require_clean`) once at the start, then spends about a minute on `setup` and the landing check before `git.fast_forward`. So a write that starts during a landing leaves the main checkout briefly dirty and the landing fails (`TASK-410`'s dirty-tree error, 2026-11-19), or the fast-forward refuses to overwrite a file the write changed, and two writes at once can collide on Git's `index.lock`. Decided with the owner 2026-11-19: serialise these with one short lock. This replaces `TASK-419`.

Decisions:

- New lock in `src/chitty/locks.py`: `MAIN_CHECKOUT_LOCK = "main-checkout.lock"`, in the same directory as the other locks (`_directory(root)`, which is `<git common dir>/chitty/run`), and a context manager `main_checkout_lock(root: Path)` built like `landing_lock`: a blocking exclusive `flock` that the kernel releases if the process dies. When `_directory(root)` is `None` (no Git repository), it yields without locking. It is not reentrant; no write nests inside another (checked 2026-11-19 by reading every `with self._all_or_nothing():` block in `store.py` and the private helpers they call, `_set_archived`, `_delete_done` and `_archive`: none calls another write).
- `Repo._all_or_nothing` in `src/chitty/store.py` holds `main_checkout_lock(self.root)` for its whole body when `self.root` is in a Git repository and is not a linked worktree (`git.is_linked_worktree`). Writes in a ticket worktree take no lock: each worktree has its own working tree, and its ticket has a run lock.
- `Repo._prepare_write` and `Repo.refresh_setup` hold the same lock around `init_repo` and the setup commit, when they reach them in the main checkout.
- Landing keeps `landing_lock` around the whole landing, as today, and takes `main_checkout_lock` only for the moments it touches the main checkout: around the first `git.require_clean(main_root)`, and around a new `git.require_clean(main_root)` followed by `git.fast_forward(main_root, branch)` on each attempt. It never holds `main_checkout_lock` during `setup`, the landing check or the rebase, so a write waits only seconds, never for a whole landing. Lock order is always `landing_lock` then `main_checkout_lock`; writes take only the second, so they cannot deadlock with a landing.
- `locks.locked_ids` lists every held `*.lock` in that directory as an ID, so it will list `main-checkout` while it is held, as it already lists `landing`. Accepted: no ticket has those IDs.
- Out of scope: lost updates when two processes edit the same ticket (run locks keep runners off each other's tickets), and Git commands a person runs by hand.
- Docs: in `docs/plan/next-action-and-runner.md`, add one bullet near the landing bullets describing the lock and the lock order as above.

Tests, new file `tests/test_main_checkout_lock.py`. Both use a holder: a Python script run with `subprocess.Popen([sys.executable, holder, lock_path, held, release])` that creates the lock's directory, opens `lock_path` (`<git common dir>/chitty/run/main-checkout.lock`; in these tests the root is the main checkout, so it is `<root>/.git/chitty/run/main-checkout.lock`, written out, not imported from `chitty.locks`, so the test also runs against the old code), takes `fcntl.flock(fd, fcntl.LOCK_EX)`, writes `held`, then waits (polling every 0.05 s, at most 30 s) until `release` exists, and exits. No property: the behaviour is the ordering of two real processes.

- `test_a_write_in_the_main_checkout_waits_for_the_lock`: a `CliTestCase` repository with Git (`git init -b main`, user name and email set), `autocommit = true` and one committed ticket `TASK-1`. Start the holder and wait for `held`. Start `subprocess.Popen([sys.executable, "-c", "from chitty.cli import main; main()", "edit", "TASK-1", "--note", "waited"], cwd=self.root)`. After 2 s, assert it is still running (`poll()` is `None`) and `git log -1 --format=%s` is unchanged. Create `release`; the edit exits 0 within 30 s and `git log -1 --format=%s` starts with `chitty: edit TASK-1`.
- In `tests/test_review_merge.py`: give the landing-check script in `setUp` a third argument, `self.logs / "hold_main"`. Inside its existing `if Path('main-late.txt').exists() or Path('review-marker').exists():` block, first, when `Path(sys.argv[3]).exists()`: start, detached, a second holder script whose arguments are the main root (read from `sys.argv[3]`) and a `held` path next to `sys.argv[3]`. It takes the same lock (`<root>/.git/chitty/run/main-checkout.lock`), writes `dirty\n` to `<root>/shared.txt`, writes `held`, sleeps 2 s, runs `git -C <root> checkout -- shared.txt`, and exits, which releases the lock. Before starting it, the check script deletes `held` if it exists (the landing may retry and run the check again), and afterwards waits for `held` at most 30 s, exiting non-zero if it never appears, so an implementation that holds the lock during the landing check fails the test instead of hanging it. New test `test_landing_waits_for_a_write_in_the_main_checkout`: `self.branch_for_review(shared="branch\n")`, write `str(self.root)` to `self.logs / "advance_main"` and to `self.logs / "hold_main"`, run `self.run_cli("run", "--mode", "review")`; it lands: the output contains `landed TASK-1`, `git show main:shared.txt` is `branch\n`, and `git status --porcelain` in the main checkout is empty. On the old code the fast-forward runs while `shared.txt` is dirty and fails, so the ticket goes to `error`.
- Guard, `test_a_write_in_a_ticket_worktree_does_not_wait`: in the same kind of repository, add a linked worktree with `git worktree add -b task-1 .worktrees/task-1`. With the holder holding the lock, `subprocess.run([sys.executable, "-c", "from chitty.cli import main; main()", "edit", "TASK-1", "--note", "no wait"], cwd=<worktree>, timeout=10)` exits 0 and `git -C <worktree> log -1 --format=%s` starts with `chitty: edit TASK-1`. It passes before the change too; it stops a worker locking every write.

## Acceptance Criteria

- [ ] The two lock tests pass; each fails against `main` before this change, the first because the edit finishes while the lock is held, the second because the ticket goes to `error` (recorded in the notes); the worktree guard passes before and after
- [ ] The existing landing tests in `tests/test_review_merge.py` and `tests/test_landing.py` still pass; `make check` passes

## Notes

Cold read 2026-11-19 (first use of the `cold-reader` agent) outcomes: the check script waits for `held` at most 30 s, so a wrong lock fails rather than hangs; it deletes a stale `held` before each attempt; a guard that ticket-worktree writes do not wait; no locking outside a Git repository; the lock path named by the common Git directory; the no-nesting claim re-checked by the planner, including the private helpers.

## History

- 2026-11-19T17:48:46Z quick-ginger-lapwing → planning
- 2026-11-19T17:49:20Z quick-ginger-lapwing: changed description
- 2026-11-19T17:51:06Z quick-ginger-lapwing: changed description, acceptance criteria, notes
