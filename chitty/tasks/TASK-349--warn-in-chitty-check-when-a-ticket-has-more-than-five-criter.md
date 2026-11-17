---
title: Warn in chitty check when a ticket has more than five criteria
status: review
created: 2026-11-16
---

## Description

`src/chitty/roles/plan.md` says about five criteria is the limit and to split larger tickets. Make `chitty check` warn about a ticket in `planning` or `todo` that has more than five criteria, then point the guide at the warning.

Add the warning in `check()` in `src/chitty/check.py`, as a `Problem` with severity `warning`, like `_markdown_warnings`. Put the limit in a module-level constant `MAX_CRITERIA = 5`. The message is exactly `<N> acceptance criteria; split tickets above 5`, where N is the count. Only status and count matter: an archived ticket in `planning` or `todo` warns too. A warning does not change the exit code of `chitty check`, and `chitty edit` keeps ignoring warnings.

Tests use Hypothesis, as `tests/test_property_next.py` does, and go in a new file `tests/test_check_criteria_limit.py`, inheriting `RepoTestCase` from `tests/support.py` and using its config, so no setup warning appears.

Out of scope: warning from `chitty edit` or `chitty add`, configuring the limit, and counting checks inside one criterion.

## Acceptance Criteria

- [x] Property test with Hypothesis: generate a set of 1 to 12 tickets, each with a status from `STATUSES` in `src/chitty/model.py`, 0 to 10 criteria whose text is ASCII letters only, and archived or not. Write each example into a fresh repository (or clear `chitty/` between examples). The set of paths with a criteria-limit warning from `check()` equals the set of tickets in `planning` or `todo` with more than `MAX_CRITERIA` criteria, each warned once with the exact message. The test fails on `main` because of the missing warning, not only because `MAX_CRITERIA` cannot be imported.
- [x] `chitty check` on a repository whose only problem is a `todo` ticket with six criteria prints a line containing `warning:` and the ticket path, and exits 0.
- [x] In `src/chitty/roles/plan.md`, `About five criteria is the limit; split larger work.` is replaced with exactly `` `chitty check` warns above five criteria; split larger work. ``, and `tests/test_guide_plan_restored.py` asserts that sentence instead of the old one. The later sentence `Split rather than exceed about five criteria.` stays. `make check` passes.

## Plan

Add a module-level criteria threshold and append warning Problems during check() for parsed tickets whose status is planning or todo and whose criterion count exceeds the threshold. Test the property across generated ticket sets in a fresh RepoTestCase repository, add CLI exit/output coverage, and update the planning guide assertion and wording.

## Notes

Review failed (tests): New findings; assert warning multiplicity and make the property test reliable under the full suite.
1: fail - A throwaway unittest run wrapping `check` to duplicate every criteria warning printed `OK` and `DUPLICATED WARNING TEST RESULT: True`: the dictionary comprehension silently collapses duplicates, so the required once-per-ticket property is not tested. Wrapping `check` to remove criteria warnings printed `FAILED (failures=1)` for a planning ticket with six criteria, confirming the missing-warning case is exercised.
2: pass - `uv run python -m unittest tests.test_cli.TestCheck.test_criteria_warning_does_not_fail_check tests.test_guide_plan_restored` printed `Ran 5 tests` and `OK`; the CLI test checks warning output, path and zero exit.
3: fail - The guide and assertion contain the required replacement, and `rg` confirms the later sentence remains. However, `make format && make check` failed: Hypothesis reported `FlakyFailure`, with a 260.48ms example exceeding the 200ms deadline on the first run and taking 157.97ms on retry. Remove the timing sensitivity and rerun the full check.

Check failed before this session: check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
520 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 597 test suites (597 total tests) across 16 workers
....................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 17:57:15 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.................E...........................................................................Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuy1myy7y...
.............................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
.../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/CLAUDE.md
..Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp04se_ut2/repo/.worktrees/task-1...
.....TASK-1: doing → review
.....no next ticket for --mode work
.........................................chitty 0.1.31 is out: run uv tool upgrade chitty
...............................landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_warning_paths_and_messages_match_property (tests.test_check_criteria_limit.TestCriteriaLimit.test_warning_paths_and_messages_match_property)
----------------------------------------------------------------------
  + Exception Group Traceback (most recent call last):
  |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/tests/test_check_criteria_limit.py", line 16, in test_warning_paths_and_messages_match_property
  |     @given(
  |
  |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
  |     raise the_error_hypothesis_found
  | hypothesis.errors.FlakyFailure: Hypothesis test_warning_paths_and_messages_match_property(self=<tests.test_check_criteria_limit.TestCriteriaLimit testMethod=test_warning_paths_and_messages_match_property>, examples=[('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', [], False),
  |  ('backlog', ['a', 'a'], False),
  |  ('backlog', [], False)]) produces unreliable results: Failed on the first call but did not on a subsequent one (1 sub-exception)
  | Failing test case: test_warning_paths_and_messages_match_property(
  |     self=<tests.test_check_criteria_limit.TestCriteriaLimit testMethod=test_warning_paths_and_messages_match_property>,
  |     examples=[('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', [], False),
  |      ('backlog', ['a', 'a'], False),
  |      ('backlog', [], False)],
  | )
  | Unreliable test timings! On an initial run, this test took 346.00ms, which exceeded the deadline of 200.00ms, but on a subsequent run it took 133.11 ms, which did not. If you expect this sort of variability in your test timings, consider turning deadlines off for this test by setting deadline=None.
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1253, in _execute_once_for_engine
    |     result = self.execute_once(data)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1187, in execute_once
    |     result = self.test_runner(data, run)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 831, in default_executor
    |     return function(data)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1144, in run
    |     return test(*args, **kwargs)
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/tests/test_check_criteria_limit.py", line 16, in test_warning_paths_and_messages_match_property
    |     @given(
    |
    |   File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-349/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1040, in test
    |     raise DeadlineExceeded(
    |         datetime.timedelta(seconds=runtime), self.settings.deadline
    |     )
    | hypothesis.errors.DeadlineExceeded: Test took 346.00ms, which exceeds the deadline of 200.00ms. If you expect test cases to take this long, you can use @settings(deadline=...) to either set a higher deadline, or to disable it with deadline=None.
    +------------------------------------

----------------------------------------------------------------------
Ran 597 tests in 26.826s

FAILED (errors=1)
make: *** [check] Error 1

```

Fixed review findings: warning assertions now preserve multiplicity with assertCountEqual, and Hypothesis deadline is disabled for filesystem-heavy examples. Focused property test passes; full make format && make check passes (597 tests). The duplicated-warning mutation now fails the multiplicity assertion. chitty fix reports existing Markdown warnings in unrelated tickets; no files changed by it.

## Summary

Implemented criteria-limit warnings and updated the guide. Property coverage includes archived tickets and now verifies one warning per ticket without timing flakiness; CLI output and exit status covered. Verified with `make format && make check` (597 tests) and focused property test. Commit: f11e338. Ready for review.

## History

- 2026-11-16T10:00:01Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:44Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:00:58Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:00:58Z kind-umber-toad planning → cold-read
- 2026-11-17T16:02:55Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:02:55Z kind-umber-toad cold-read → planning
- 2026-11-17T16:04:10Z kind-umber-toad planning → todo
- 2026-11-17T17:45:59Z rosy-zinc-jay todo → doing
- 2026-11-17T17:46:19Z rosy-zinc-jay: wrote the plan
- 2026-11-17T17:50:08Z rosy-zinc-jay: changed summary; ticked acceptance criteria
- 2026-11-17T17:50:08Z rosy-zinc-jay doing → review
- 2026-11-17T17:52:48Z intrepid-dusky-lapwing: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-17T17:52:48Z intrepid-dusky-lapwing review → doing
- 2026-11-17T17:57:32Z quick-bronze-kestrel: changed notes
- 2026-11-17T17:59:04Z quick-bronze-kestrel: changed notes, summary; ticked acceptance criteria
- 2026-11-17T17:59:04Z quick-bronze-kestrel doing → review
