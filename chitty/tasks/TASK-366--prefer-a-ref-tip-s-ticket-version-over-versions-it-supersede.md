---
title: Prefer a ref tip's ticket version over versions it superseded
status: error
labels:
  - bug
created: 2026-11-17
---

## Description

Seen 2026-11-17 landing `TASK-326` and `TASK-356` by hand. `git.historical_files` picks, for each path, the newest commit that touched it in the whole history reachable from any ref (`_latest_changes` in `src/chitty/git.py`, `git log --topo-order <all refs> -- chitty/tasks`), not the version at each ref tip. After `main` was merged into the ticket branch with the conflict resolved to the branch side (`status: done`) and `main` fast-forwarded, `main`'s tip held `done`, but `chitty show` returned the older `review → error` version committed on `main` at 17:25:03, because it was newer than the branch's `done` commit at 17:24:56 and the TREESAME merge is not listed for the path. `chitty edit` then refused: "TASK-326's latest committed version is on branch task-343", a branch that had only merged an older `main`. Workaround used: a new commit on `main` touching the file. The version on a ref tip should beat any version that tip has superseded: an ancestor's version must never win over a descendant's.

## Plan

Change historical file selection to compare each path only among commits that are maximal in the ancestry partial order across refs: a descendant version must supersede its ancestors regardless of commit timestamps. Add a regression test with divergent refs and a merge whose tip retains the branch-side blob despite a newer-timestamp ancestor commit; verify current tip content/ref wins. Run regression against old behavior first, then implement, format, check, and commit with Task trailer.

## Notes

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
529 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 618 test suites (618 total tests) across 16 workers
............................................................................................................................................................................................................................................................................................................................................F.F...........................................F.......F.......━━━━ chitty run · 22:49:57 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.........F.F........................F...................................................F.FF....FF.F........Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmphe9xctfy...
.......F.................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
....../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/CLAUDE.md
..Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/.worktrees/task-1...
....TASK-1: doing → review
.......no next ticket for --mode work
..................................F.....chitty 0.1.31 is out: run uv tool upgrade chitty
................................
======================================================================
test_pending_landing_failure_is_completed_by_a_later_run (tests.test_landing.TestLanding.test_pending_landing_failure_is_completed_by_a_later_run)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_landing.py", line 238, in test_pending_landing_failure_is_completed_by_a_later_run
    failed = self.run_cli("run", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : TASK-1: todo → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpksdubiu8/repo/.worktrees/task-1...


======================================================================
test_pending_landing_failure_stops_before_later_ticket (tests.test_landing.TestLanding.test_pending_landing_failure_stops_before_later_ticket)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_landing.py", line 193, in test_pending_landing_failure_stops_before_later_ticket
    with self.assertRaisesRegex(ChittyError, "unfinished"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ChittyError not raised

======================================================================
test_pending_tickets_land_in_order_one_per_run (tests.test_landing.TestLanding.test_pending_tickets_land_in_order_one_per_run)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_landing.py", line 171, in test_pending_tickets_land_in_order_one_per_run
    assert first is not None
           ^^^^^^^^^^^^^^^^^
AssertionError

======================================================================
test_list_git_trace_is_constant_in_task_count (tests.test_list_performance.TestListPerformance.test_list_git_trace_is_constant_in_task_count)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_list_performance.py", line 15, in test_list_git_trace_is_constant_in_task_count
    self.assertEqual(counts[0], counts[1])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 18 != 26

======================================================================
test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review (tests.test_next.TestNext.test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_next.py", line 1467, in test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        "error",
        ^^^^^^^^
    )
    ^
AssertionError: 'doing' != 'error'
- doing
+ error


======================================================================
test_run_from_another_worktree_uses_the_branch_not_main (tests.test_next.TestNext.test_run_from_another_worktree_uses_the_branch_not_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_next.py", line 2336, in test_run_from_another_worktree_uses_the_branch_not_main
    result = self.run_cli("run", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : TASK-1: doing → blocked
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/CLAUDE.md
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/.worktrees/task-1...


======================================================================
test_todo_dependency_must_be_done_on_main (tests.test_next.TestNext.test_todo_dependency_must_be_done_on_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_next.py", line 185, in test_todo_dependency_must_be_done_on_main
    with self.assertRaisesRegex(ChittyError, "no next ticket"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ChittyError not raised

======================================================================
test_a_recorded_resolution_is_not_replayed_into_the_review (tests.test_review_merge.TestReviewMerge.test_a_recorded_resolution_is_not_replayed_into_the_review)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 371, in test_a_recorded_resolution_is_not_replayed_into_the_review
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_agent_and_setup_see_the_branch_merged_with_main (tests.test_review_merge.TestReviewMerge.test_agent_and_setup_see_the_branch_merged_with_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 320, in test_agent_and_setup_see_the_branch_merged_with_main
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_an_unfinished_merge_fails_loudly_without_a_status_change (tests.test_review_merge.TestReviewMerge.test_an_unfinished_merge_fails_loudly_without_a_status_change)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 525, in test_an_unfinished_merge_fails_loudly_without_a_status_change
    result = self.run_cli("run", "--mode", "review", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 1 : no next ticket for --mode review


======================================================================
test_change_outside_managed_block_passes_review (tests.test_review_merge.TestReviewMerge.test_change_outside_managed_block_passes_review)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 227, in test_change_outside_managed_block_passes_review
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_check_that_dirties_review_worktree_blocks_before_agent (tests.test_review_merge.TestReviewMerge.test_check_that_dirties_review_worktree_blocks_before_agent)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 428, in test_check_that_dirties_review_worktree_blocks_before_agent
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_conflict_moves_the_ticket_to_doing_without_starting_the_agent (tests.test_review_merge.TestReviewMerge.test_conflict_moves_the_ticket_to_doing_without_starting_the_agent)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 337, in test_conflict_moves_the_ticket_to_doing_without_starting_the_agent
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_failing_check_after_main_advances_preserves_main_and_worktree (tests.test_review_merge.TestReviewMerge.test_failing_check_after_main_advances_preserves_main_and_worktree)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 303, in test_failing_check_after_main_advances_preserves_main_and_worktree
    self.assertIn("landing check exited with status 7", notes)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'landing check exited with status 7' not found in ''

======================================================================
test_reads_newer_task_state_from_another_branch_at_the_same_second (tests.test_store.TestStore.test_reads_newer_task_state_from_another_branch_at_the_same_second)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_store.py", line 113, in test_reads_newer_task_state_from_another_branch_at_the_same_second
    self.assertEqual(task.task.frontmatter.status, "doing")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'todo' != 'doing'
- todo
+ doing


----------------------------------------------------------------------
Ran 618 tests in 22.359s

FAILED (failures=15)
make: *** [check] Error 15

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-366`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
529 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 618 test suites (618 total tests) across 16 workers
............................................................................................................................................................................................................................................................................................................................................F.F...........................................F.......F.......━━━━ chitty run · 22:49:57 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.........F.F........................F...................................................F.FF....FF.F........Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmphe9xctfy...
.......F.................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
....../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/CLAUDE.md
..Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpp09xdltc/repo/.worktrees/task-1...
....TASK-1: doing → review
.......no next ticket for --mode work
..................................F.....chitty 0.1.31 is out: run uv tool upgrade chitty
................................
======================================================================
test_pending_landing_failure_is_completed_by_a_later_run (tests.test_landing.TestLanding.test_pending_landing_failure_is_completed_by_a_later_run)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_landing.py", line 238, in test_pending_landing_failure_is_completed_by_a_later_run
    failed = self.run_cli("run", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : TASK-1: todo → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpksdubiu8/repo/.worktrees/task-1...


======================================================================
test_pending_landing_failure_stops_before_later_ticket (tests.test_landing.TestLanding.test_pending_landing_failure_stops_before_later_ticket)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_landing.py", line 193, in test_pending_landing_failure_stops_before_later_ticket
    with self.assertRaisesRegex(ChittyError, "unfinished"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ChittyError not raised

======================================================================
test_pending_tickets_land_in_order_one_per_run (tests.test_landing.TestLanding.test_pending_tickets_land_in_order_one_per_run)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_landing.py", line 171, in test_pending_tickets_land_in_order_one_per_run
    assert first is not None
           ^^^^^^^^^^^^^^^^^
AssertionError

======================================================================
test_list_git_trace_is_constant_in_task_count (tests.test_list_performance.TestListPerformance.test_list_git_trace_is_constant_in_task_count)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_list_performance.py", line 15, in test_list_git_trace_is_constant_in_task_count
    self.assertEqual(counts[0], counts[1])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 18 != 26

======================================================================
test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review (tests.test_next.TestNext.test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_next.py", line 1467, in test_run_adds_worktree_for_existing_branch_and_refuses_unbranched_review
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        Repo.open(worktree).find(Repo.open(worktree).resolve("TASK-1")).task.frontmatter.status,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        "error",
        ^^^^^^^^
    )
    ^
AssertionError: 'doing' != 'error'
- doing
+ error


======================================================================
test_run_from_another_worktree_uses_the_branch_not_main (tests.test_next.TestNext.test_run_from_another_worktree_uses_the_branch_not_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_next.py", line 2336, in test_run_from_another_worktree_uses_the_branch_not_main
    result = self.run_cli("run", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : TASK-1: doing → blocked
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/CLAUDE.md
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplt55dxj_/repo/.worktrees/task-1...


======================================================================
test_todo_dependency_must_be_done_on_main (tests.test_next.TestNext.test_todo_dependency_must_be_done_on_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_next.py", line 185, in test_todo_dependency_must_be_done_on_main
    with self.assertRaisesRegex(ChittyError, "no next ticket"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ChittyError not raised

======================================================================
test_a_recorded_resolution_is_not_replayed_into_the_review (tests.test_review_merge.TestReviewMerge.test_a_recorded_resolution_is_not_replayed_into_the_review)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 371, in test_a_recorded_resolution_is_not_replayed_into_the_review
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_agent_and_setup_see_the_branch_merged_with_main (tests.test_review_merge.TestReviewMerge.test_agent_and_setup_see_the_branch_merged_with_main)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 320, in test_agent_and_setup_see_the_branch_merged_with_main
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_an_unfinished_merge_fails_loudly_without_a_status_change (tests.test_review_merge.TestReviewMerge.test_an_unfinished_merge_fails_loudly_without_a_status_change)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 525, in test_an_unfinished_merge_fails_loudly_without_a_status_change
    result = self.run_cli("run", "--mode", "review", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 1 : no next ticket for --mode review


======================================================================
test_change_outside_managed_block_passes_review (tests.test_review_merge.TestReviewMerge.test_change_outside_managed_block_passes_review)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 227, in test_change_outside_managed_block_passes_review
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_check_that_dirties_review_worktree_blocks_before_agent (tests.test_review_merge.TestReviewMerge.test_check_that_dirties_review_worktree_blocks_before_agent)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 428, in test_check_that_dirties_review_worktree_blocks_before_agent
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_conflict_moves_the_ticket_to_doing_without_starting_the_agent (tests.test_review_merge.TestReviewMerge.test_conflict_moves_the_ticket_to_doing_without_starting_the_agent)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 337, in test_conflict_moves_the_ticket_to_doing_without_starting_the_agent
    result = self.run_cli("run", "--mode", "review")
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3 != 0 : no next ticket for --mode review


======================================================================
test_failing_check_after_main_advances_preserves_main_and_worktree (tests.test_review_merge.TestReviewMerge.test_failing_check_after_main_advances_preserves_main_and_worktree)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_review_merge.py", line 303, in test_failing_check_after_main_advances_preserves_main_and_worktree
    self.assertIn("landing check exited with status 7", notes)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'landing check exited with status 7' not found in ''

======================================================================
test_reads_newer_task_state_from_another_branch_at_the_same_second (tests.test_store.TestStore.test_reads_newer_task_state_from_another_branch_at_the_same_second)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-366/tests/test_store.py", line 113, in test_reads_newer_task_state_from_another_branch_at_the_same_second
    self.assertEqual(task.task.frontmatter.status, "doing")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'todo' != 'doing'
- todo
+ doing


----------------------------------------------------------------------
Ran 618 tests in 22.359s

FAILED (failures=15)
make: *** [check] Error 15

```
````

Obsolete 2026-11-18: the one-authoritative-copy model (`docs/plan/ticket-state.md`, `TASK-376`) replaces the history scan this ticket patched. Archived.

## History

- 2026-11-17T19:53:03Z kind-umber-toad → todo
- 2026-11-17T22:40:24Z vivid-amber-vole todo → doing
- 2026-11-17T22:40:39Z vivid-amber-vole: wrote the plan
- 2026-11-17T22:50:14Z youthful-silver-ibis: changed notes
- 2026-11-17T22:50:14Z youthful-silver-ibis doing → error
- 2026-11-18T16:25:12Z lively-quartz-crane: changed notes
