---
title: Refuse a repair that returns a ticket to review with no change beyond its ticket files
status: done
created: 2026-11-16
---

## Description

A repair agent can end an `error` ticket in `review` with nothing to review. Every `chitty edit` autocommits, so "the branch has commits beyond `main`" is satisfied by the agent's own status change; and for a ticket whose branch was missing (`TASK-326`), `_worktree` creates a fresh branch from `main`. Seen by the `TASK-326` cold read: a repair that only ran `chitty edit 1 -s review` printed `TASK-1: error → review`.

Refuse that. When a repair session ends with the ticket in `review`, and the branch changes no file outside the ticket directories compared with its merge base with `main` (committed changes only), raise `RepairError` with the text `repair agent returned <ID> to review with no change beyond its ticket files` before the final `main_repo.edit` in `_run_session` (around the `if repairing:` block in `src/chitty/run.py`), so the ticket stays `error`. A repair ending in `blocked` is unaffected.

Put the decision in a pure function in `src/chitty/run.py`:

`has_work_beyond_tickets(changed_paths: Iterable[PurePosixPath], ticket_directories: Iterable[PurePosixPath]) -> bool`

true when some changed path is outside every ticket directory, compared by path parts (`PurePosixPath.is_relative_to`), never by string prefix. The ticket directories are `context.directory` for each of `repo.contexts()`, made relative to the repo root; archive directories sit inside them. Add a git helper in `src/chitty/git.py`, `changed_paths(root, base, branch) -> list[PurePosixPath]`, that runs `git diff -z --no-renames --name-only <base>...<branch>` and splits on NUL: without `--no-renames` a file moved from code into a ticket directory shows only its new path, and without `-z` non-ASCII names come back quoted. The branch is `str(action.id).lower()` and the base `main_repo.config.main_branch`.

After a refusal the worktree keeps whatever the agent left, including an uncommitted status change; the next `chitty run --errors` reuses it and the repair agent sees it. That is intended.

Existing repair tests that end in `review` with a ticket-only commit must give the branch a real change, for example by committing a code file in the fake agent: `test_run_check_failure_on_error_ticket_starts_repair_agent` in `tests/test_next.py` and the repair test near line 2374 of the same file.

Files: `src/chitty/run.py`, `src/chitty/git.py`, `tests/test_next.py`, new `tests/test_property_repair_work.py` and `tests/test_repair_requires_work.py`.

## Acceptance Criteria

- [x] Hypothesis properties in `tests/test_property_repair_work.py`, with paths built from one to four non-empty segments, no `..` and no leading `/`, including paths inside, outside, prefix-alike (`chitty/tasksX/a.md` against `chitty/tasks`), equal to a directory, and empty sets: `has_work_beyond_tickets` is true exactly when some path is not inside any ticket directory; shuffling or duplicating either input does not change the result; adding a path never turns true into false. First add the function raising `NotImplementedError`; the test fails with that before the change.
- [x] Fake-agent tests in `tests/test_repair_requires_work.py`, one subtest per case, on an `error` ticket whose branch exists at the tip of `main` (the state `_worktree` also creates for a missing branch): the agent sets `review` through `chitty edit` only; writes `status: review` to the ticket file without committing; commits a code file then sets `review`; sets `blocked`. Only the code-file case ends in `review`; the first two make `chitty run --errors` exit non-zero with the `RepairError` text and leave the ticket `error`; `blocked` ends in `blocked`. The first two cases fail before the change. The two repair tests in `tests/test_next.py` are updated to commit a code file and pass.
- [x] Real-git tests of `changed_paths`: a branch that moves `src/a.py` to `chitty/tasks/a.md` returns both paths; a branch adding `chitty/tasks/é.md` returns that path unquoted. `make check` passes.

## Plan

Add a pure path-based work detector and a NUL-delimited git diff helper. In repair completion, before persisting final status to main, reject review when the repair branch diff from configured main has no paths outside all repository ticket directories. Add property tests, real-git helper tests, and fake-agent repair cases; update existing repair fixtures to commit real code work.

## Notes

Verified the repair refusal regression tests fail without the refusal: temporarily bypassing the path check caused the ticket-only edit and uncommitted-status cases to succeed unexpectedly. Restored the check and reran the focused tests successfully. make check passes.

Review failed (tests): Correct the fake-agent scenarios and rerun their regression checks.
1: pass - `make check` passed; replacing the function in memory with a `NotImplementedError` stub made all three property tests error.
2: fail - Newly discovered: `tests/test_repair_requires_work.py` writes review directly before every case, including the purported `chitty edit`-only case, so it does not exercise the required CLI-only handoff. The code case also writes and commits review before committing code, rather than committing code then setting review. Construct the cases in the specified order and demonstrate that both no-work cases fail without the refusal. The existing focused suite printed `Ran 16 tests` and `OK`; the worker reported the bypass regression, but it does not establish the missing CLI-only scenario.
3: pass - `tests.test_git` exercised the real rename and Unicode paths in the focused run, which printed `OK`; `make check` passed 617 tests.

The revised regression fixture still fails: the CLI-only case ends with the main ticket in review instead of triggering the expected refusal, while the code-change case ends in error instead of review. The generated fake agent invokes chitty edit but the test does not currently establish which repository that command edits or why the repair state differs. Need inspect run_cli/worktree environment and revise the fake-agent setup so each case performs the specified action inside the repair worktree; acceptance criterion 2 cannot be verified until this is resolved.

Planning, 2026-11-17: no ticket defect found. Likely cause of the fixture confusion: `chitty show` resolves a ticket across branches and prefers the newest committed version, so after a refused repair whose agent committed `review` on the repair branch it reports `review` although `main` still says `error` (see `TASK-366`). Assert the status in the main checkout's ticket file (parse it, or `git show main:<path>`), not with `chitty show`. The worktree has an uncommitted change to `tests/test_repair_requires_work.py` from the last session.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
530 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 621 test suites (621 total tests) across 16 workers
.........................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 22:34:58 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
........................................................................................F......................F..Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpqc11shkd...
.......................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
....../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/.worktrees/task-1...
.....TASK-1: doing → review
...no next ticket for --mode work
............................................chitty 0.1.31 is out: run uv tool upgrade chitty
...............................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_repair_requires_committed_work_outside_ticket_directories (tests.test_repair_requires_work.TestRepairRequiresWork.test_repair_requires_committed_work_outside_ticket_directories) (case='edit')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 12, in test_repair_requires_committed_work_outside_ticket_directories
    case._run_repair_case(case_name)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 56, in _run_repair_case
    self.assertEqual(self.json("show", ticket)["status"], "error")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'review' != 'error'
- review
+ error


======================================================================
test_repair_requires_committed_work_outside_ticket_directories (tests.test_repair_requires_work.TestRepairRequiresWork.test_repair_requires_committed_work_outside_ticket_directories) (case='code')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 12, in test_repair_requires_committed_work_outside_ticket_directories
    case._run_repair_case(case_name)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 60, in _run_repair_case
    self.assertEqual(self.json("show", ticket)["status"], expected, result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'error' != 'review'
- error
+ review
 : /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/CLAUDE.md
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 621 tests in 39.140s

FAILED (failures=2)
make: *** [check] Error 2

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-364`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
530 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 621 test suites (621 total tests) across 16 workers
.........................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 22:34:58 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
........................................................................................F......................F..Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpqc11shkd...
.......................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
....../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/CLAUDE.md
...Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyyi96fmf/repo/.worktrees/task-1...
.....TASK-1: doing → review
...no next ticket for --mode work
............................................chitty 0.1.31 is out: run uv tool upgrade chitty
...............................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_repair_requires_committed_work_outside_ticket_directories (tests.test_repair_requires_work.TestRepairRequiresWork.test_repair_requires_committed_work_outside_ticket_directories) (case='edit')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 12, in test_repair_requires_committed_work_outside_ticket_directories
    case._run_repair_case(case_name)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 56, in _run_repair_case
    self.assertEqual(self.json("show", ticket)["status"], "error")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'review' != 'error'
- review
+ error


======================================================================
test_repair_requires_committed_work_outside_ticket_directories (tests.test_repair_requires_work.TestRepairRequiresWork.test_repair_requires_committed_work_outside_ticket_directories) (case='code')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 12, in test_repair_requires_committed_work_outside_ticket_directories
    case._run_repair_case(case_name)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-364/tests/test_repair_requires_work.py", line 60, in _run_repair_case
    self.assertEqual(self.json("show", ticket)["status"], expected, result.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'error' != 'review'
- error
+ review
 : /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/CLAUDE.md
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpej5gw_8d/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 621 tests in 39.140s

FAILED (failures=2)
make: *** [check] Error 2

```
````

Error repair, 2026-11-17: the runner's pre-session check failed on the uncommitted fixture rewrite in `tests/test_repair_requires_work.py`. Two causes, both in the test: the `code` agent committed with the one-paragraph message `Task: TASK-1`, which `TASK-346`'s trailer check (now on `main`) treats as no trailer; and the refused cases asserted with `chitty show`, which returns the repair branch's committed `review` while `main` stays `error`. Fixed both in the test; `make check` passes on the branch. With the refusal disabled (`if False and ...` at `src/chitty/run.py:480`), exactly the `edit` and `uncommitted` cases fail.

Reviewed: The earlier fixture-order finding is resolved; the fake agent now uses the specified actions and order.
1: pass - make check passed; the earlier review recorded all three property tests erroring with a NotImplementedError stub.
2: pass - make check passed 627 tests including the four fake-agent cases and updated repair fixtures. The worker recorded that disabling the refusal makes exactly the edit and uncommitted cases fail.
3: pass - make check passed the real-git rename and Unicode test; replacing the helper in memory with git diff --name-only made the rename assertion fail, showing only chitty/tasks/a.md instead of both paths.

## Summary

Implemented committed diff-path detection for repair handoffs. Verification: make check passes; focused repair, property, and real-git tests pass. Regression evidence: disabling the check makes the two no-work fake-agent cases fail as expected. Changes committed in add740b with Task: TASK-364. No follow-ups.

## History

- 2026-11-16T17:08:51Z open-russet-eel → planning
- 2026-11-16T17:09:05Z open-russet-eel: changed owner
- 2026-11-16T17:09:05Z open-russet-eel planning → cold-read
- 2026-11-16T17:10:33Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T17:10:33Z open-russet-eel cold-read → planning
- 2026-11-16T17:10:35Z open-russet-eel: changed owner
- 2026-11-16T17:10:35Z open-russet-eel planning → todo
- 2026-11-17T18:25:30Z calm-teal-ibis todo → doing
- 2026-11-17T18:25:46Z calm-teal-ibis: wrote the plan
- 2026-11-17T18:35:31Z calm-teal-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-17T18:35:31Z calm-teal-ibis doing → review
- 2026-11-17T18:37:35Z able-navy-badger: changed acceptance criteria, notes
- 2026-11-17T18:37:35Z able-navy-badger review → doing
- 2026-11-17T18:40:43Z able-ochre-kestrel: changed owner, notes
- 2026-11-17T18:40:43Z able-ochre-kestrel doing → planning
- 2026-11-17T19:59:36Z kind-umber-toad: changed notes
- 2026-11-17T20:22:36Z kind-umber-toad: changed owner
- 2026-11-17T20:22:36Z kind-umber-toad planning → todo
- 2026-11-17T22:35:27Z open-dusky-raven: changed notes
- 2026-11-17T22:35:27Z open-dusky-raven todo → error
- 2026-11-17T22:48:42Z kind-umber-toad: changed notes; ticked acceptance criteria
- 2026-11-17T22:48:42Z kind-umber-toad error → review
- 2026-11-18T09:30:45Z youthful-lilac-badger: changed notes
- 2026-11-18T09:30:45Z youthful-lilac-badger review → done
