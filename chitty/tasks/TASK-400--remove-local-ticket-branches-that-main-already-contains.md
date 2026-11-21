---
title: Remove local ticket branches that `main` already contains
status: doing
depends_on:
  - TASK-396
parent: TASK-376
created: 2026-11-18
---

## Description

Under the one-authoritative-copy model (`docs/plan/ticket-state.md`, "Planning decisions"; on branch `plan/ticket-state` until it lands on `main`), a ticket branch whose tip `main` contains is merged or stale, and reads ignore it (`TASK-377` rule 2). The owner decided on 2026-11-18 that such branches should go: if a branch equals `main`, or is behind it (which a rebase would turn into equal), delete it. Reads never do this; the runner does, as a clean-up step. (None of the nine local `task-*` branches was merged on 2026-11-18, but landed branches left behind by a failed clean-up and branches made but never worked will be.)

Starts after `TASK-396` (`git.is_ancestor`) lands.

Decisions:

- At the start of every `chitty run` (before `_land_pending` and selection), under `locks.landing_lock` (so it cannot race a landing between its fast-forward and its worktree removal), after `git worktree prune` (so a worktree whose directory was deleted by hand is forgotten rather than crashing the run), the runner removes each local ticket branch (a local branch named a configured context prefix plus `-<suffix>`, lower-cased: `task-5`, `human-12`) whose tip `main` contains, using `git.is_ancestor(root, <branch tip>, <main tip>)`: first its linked worktree, if any, then the branch (`git.remove_worktree`, `git.delete_branch`). It prints `removed merged branch <b>` to stderr for each.
- It leaves a branch alone, printing `kept merged branch <b>: <reason>`, when its ticket's run lock is held (`locks.is_locked`: a run in another session may have just made the branch from `main`), when its worktree has uncommitted or untracked files, or a merge or rebase in progress, or is the main checkout, or when removing the worktree or branch raises `ChittyError` (the reason is the error; the run carries on). Ignored files (such as `.venv/`) do not keep a branch: ticket worktrees are the runner's disposable workspaces.
- It also keeps a merged branch whose ticket exists and is not `done`, printing `kept merged branch <b>: <ID> is <status>` (status from `Repo.lookup(<ID>)`). Only branches of `done` tickets, archived or not, and of IDs no ticket has, are removed. Decided 2026-11-20 after a worker found that removing the branch of a `review` ticket makes the runner error it (a review needs its branch), and that runner tests and real runs create a `doing` ticket's branch at `main`'s tip; such branches are harmless, because work reuses them.
- Remote-tracking branches are never deleted: they are not this machine's.
- A branch with commits `main` lacks is left alone, whatever its ticket says.
- Update `docs/plan/next-action-and-runner.md` with the clean-up step.

Tests: real-Git runner tests in a new `tests/test_run_removes_merged_branches.py`, in the style of `tests/test_landing.py` (configured `setup` and `check`, fake agent), with `git init -b main`. No property: a fixed set of branch states, each in the criteria.

Fixtures for criterion 2, each its own test: run lock held: hold `locks.run_lock(root, "TASK-<n>")` (`src/chitty/locks.py`) in the test process across the `chitty run` call; uncommitted file: write an untracked `x.txt` in the branch's worktree; rebase in progress: in the worktree, commit a change to `a.txt` that conflicts with a commit on `main`, then `git rebase main` and leave it stopped; merge in progress: the same conflict with `git merge main` stopped; deleted worktree: `shutil.rmtree` the worktree directory before `chitty run`. For the rebase and merge fixtures the branch is not merged while stopped, so assert only that the run completes and the branch still exists. Also add to `tests/test_run_repair_on_branch.py`, in the test that creates an `error` ticket's branch at `main`'s tip, an assertion that stderr contains `kept merged branch task-<n>: TASK-<n> is error` and not `removed merged branch` (comparing tip SHAs would not show it: a branch recreated from `main` has the same tip).

## Acceptance Criteria

- [ ] `chitty run` removes, for `done` tickets, a local `task-<n>` equal to `main` with a clean linked worktree (both removed) and one behind `main` with no worktree, and a merged branch for an ID no ticket has, and prints `removed merged branch` for each; this fails before the change
- [ ] It keeps, with a `kept merged branch` line, a merged branch for each non-`done` status (`todo`, `doing`, `review`, `error`, `blocked`), each printing `<ID> is <status>`, a merged branch whose run lock is held, one whose worktree has an uncommitted file, one with a rebase in progress, and one with a merge in progress; it never removes a branch ahead of `main`, a non-ticket branch such as `feature`, or a remote-tracking `origin/task-<n>`; a worktree whose directory was deleted by hand does not stop the run
- [ ] `docs/plan/next-action-and-runner.md` says the clean-up runs at the start of `chitty run`, before pending landings, under the landing lock, lists the reasons a merged branch is kept, and gives the `removed merged branch` and `kept merged branch` lines; `make check` passes

## Plan

Retain merged branches for existing non-done tickets, remove eligible unknown and done ticket branches, and verify the specified real-Git cases before documenting and checking the change.

## Notes

Planning issue discovered: the required startup cleanup deletes every local ticket branch whose tip is contained by main, including branches for tickets already in review. The existing runner requires a branch/worktree to review and changes such tickets to error when missing; therefore a routine chitty run can delete the branch and then fail the same ticket during selection. The ticket does not specify whether such tickets should be exempt, returned to a workable status/recreated from main, or treated as an expected runner error. Existing runner tests also assume newly created equal-to-main ticket branches survive startup, so the required cleanup changes their expected behavior. Please decide the selection/review behavior after cleanup and update acceptance/tests accordingly.

Planning 2026-11-20: the review-state question in the earlier notes is resolved in the Description (keep merged branches of tickets that are not `done`). The branch's partial code predates it: it skips unknown IDs and has no status rule; fix both. Branch rebased onto `main` (old tip tagged `task-400-before-rebase`). Resumed as `doing` because the branch holds partial work.

Check failed before this session: check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
682 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 868 test suites (868 total tests) across 16 workers
..................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi1u33s9f/repo/chitty/tasks/TASK-1--one.md actor test-agent
...............................................................━━━━ chitty run · 00:13:27 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.................F.......F..F....F................/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
.................FE...........................E.....................................................................................................kill: 18199: No such process
..............kill: 21177: No such process
...............................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
............/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpof1wtdpz/repo/.worktrees/task-1...
Check passed; work agent is working on TASK-1...
....TASK-1: doing → review
E...E./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfxnc9moi/repo/CLAUDE.md
no next ticket for --mode work
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3yewooys/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppmqxjl53/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpya8nxsb7/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp3xrij584/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1o60fpw0/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpee26k9ru/repo/CLAUDE.md
....................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
.............................Flanded TASK-1
landed TASK-2
landed TASK-1
landed TASK-1

======================================================================
test_run_runs_setup_before_claim_and_leaves_review_unchanged (tests.test_next.TestNext.test_run_runs_setup_before_claim_and_leaves_review_unchanged)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 2297, in test_run_runs_setup_before_claim_and_leaves_review_unchanged
    review_prompt = (worktree / "agent-arguments-review").read_text()
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 546, in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_abc.py", line 632, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp4e8_6g5y/repo/.worktrees/task-1/agent-arguments-review'

======================================================================
test_run_uses_committed_change_from_ticket_worktree (tests.test_next.TestNext.test_run_uses_committed_change_from_ticket_worktree)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 1104, in git
    return subprocess.run(
           ~~~~~~~~~~~~~~^
        ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ).stdout
    ^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'worktree', 'remove', '--force', '/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpoxw0tvpz/ticket-worktree']' returned non-zero exit status 128.

======================================================================
test_unqualified_work_and_review_select_independent_models (tests.test_run_model_defaults.TestRunModelDefaults.test_unqualified_work_and_review_select_independent_models)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_run_model_defaults.py", line 88, in test_unqualified_work_and_review_select_independent_models
    self.run_ticket(status="review", agent="chosen", unqualified=True),
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_run_model_defaults.py", line 81, in run_ticket
    return (self.root / f".worktrees/task-{ticket.split('-')[1]}/invocation").read_text()
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 546, in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_abc.py", line 632, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuuajlvmn/repo/.worktrees/task-2/invocation'

======================================================================
test_review_ticket_gets_review_mode (tests.test_run_repair_mode.TestRunRepairMode.test_review_ticket_gets_review_mode)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_run_repair_mode.py", line 39, in test_review_ticket_gets_review_mode
    self.assertEqual(self.invocations_seen()[0], ["review", ticket])
                     ~~~~~~~~~~~~~~~~~~~~~~~^^^
IndexError: list index out of range

======================================================================
test_run_mode_selects_only_its_own_tickets_and_is_not_forwarded (tests.test_next.TestNext.test_run_mode_selects_only_its_own_tickets_and_is_not_forwarded)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 517, in test_run_mode_selects_only_its_own_tickets_and_is_not_forwarded
    self.assertEqual(reviewed.stdout, f"{review}: review → blocked\n")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'TASK-2: review → error\n' != 'TASK-2: review → blocked\n'
- TASK-2: review → error
?                   ^^^^
+ TASK-2: review → blocked
?                  +++++ ^


======================================================================
test_run_overlaps_one_worker_and_one_reviewer (tests.test_next.TestNext.test_run_overlaps_one_worker_and_one_reviewer)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 642, in test_run_overlaps_one_worker_and_one_reviewer
    self.assertEqual(review_task.frontmatter.status, "done")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'error' != 'done'
- error
+ done


======================================================================
test_run_rejects_lost_ticket_when_worktree_and_branch_are_removed (tests.test_next.TestNext.test_run_rejects_lost_ticket_when_worktree_and_branch_are_removed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 862, in test_run_rejects_lost_ticket_when_worktree_and_branch_are_removed
    result = self.run_cli("run", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : TASK-2: review → error
removed merged branch task-2


======================================================================
test_run_reports_status_when_agent_removes_worktree_but_keeps_branch (tests.test_next.TestNext.test_run_reports_status_when_agent_removes_worktree_but_keeps_branch)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 814, in test_run_reports_status_when_agent_removes_worktree_but_keeps_branch
    self.assertEqual(result.stdout, "TASK-2: review → done\n")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'TASK-2: review → error\n' != 'TASK-2: review → done\n'
- TASK-2: review → error
?                   ----
+ TASK-2: review → done
?                  +++


======================================================================
test_run_uses_committed_change_from_ticket_worktree (tests.test_next.TestNext.test_run_uses_committed_change_from_ticket_worktree)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_next.py", line 703, in test_run_uses_committed_change_from_ticket_worktree
    self.assertEqual(result.stdout, "TASK-1: doing → blocked\n")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'TASK-1: doing → error\n' != 'TASK-1: doing → blocked\n'
- TASK-1: doing → error
?                  ^^^^
+ TASK-1: doing → blocked
?                 +++++ ^


======================================================================
test_concurrent_reviewers_take_different_tickets (tests.test_run_lock.TestRunLock.test_concurrent_reviewers_take_different_tickets)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_run_lock.py", line 240, in test_concurrent_reviewers_take_different_tickets
    self.wait_for(*(self.logs / f"{ticket}.started" for ticket in tickets))
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-400/tests/test_run_lock.py", line 107, in wait_for
    self.assertLess(time.monotonic(), deadline, f"timed out waiting for {paths}")
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 302314.136709083 not less than 302314.132140916 : timed out waiting for (PosixPath('/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxf9ry_lh/logs/TASK-1.started'), PosixPath('/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxf9ry_lh/logs/TASK-2.started'))

----------------------------------------------------------------------
Ran 868 tests in 291.624s

FAILED (failures=6, errors=4)
make: *** [check] Error 10

```

Regression evidence: the repair test failed against the existing cleanup because it removed the error branch; it passes with the status rule. The removal test failed with the previous unknown-ID skip restored and passes with that skip removed.

## History

- 2026-11-18T18:00:02Z lively-quartz-crane → backlog
- 2026-11-18T18:00:04Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-18T18:00:04Z lively-quartz-crane backlog → cold-read
- 2026-11-18T18:02:13Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T18:02:13Z lively-quartz-crane cold-read → planning
- 2026-11-18T18:02:15Z lively-quartz-crane planning → todo
- 2026-11-18T23:14:01Z golden-quartz-heron todo → doing
- 2026-11-18T23:15:19Z golden-quartz-heron: wrote the plan
- 2026-11-18T23:18:59Z golden-quartz-heron: changed owner, notes
- 2026-11-18T23:18:59Z golden-quartz-heron doing → planning
- 2026-11-20T23:19:59Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:19:59Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:24:27Z quick-pearl-lapwing: changed description, acceptance criteria, notes
- 2026-11-20T23:24:27Z quick-pearl-lapwing cold-read → doing
- 2026-11-20T23:25:08Z quick-pearl-lapwing: changed description
- 2026-11-21T00:17:20Z jolly-ochre-lapwing: changed notes
- 2026-11-21T00:18:09Z jolly-ochre-lapwing: wrote the plan
- 2026-11-21T00:21:33Z jolly-ochre-lapwing: changed notes
