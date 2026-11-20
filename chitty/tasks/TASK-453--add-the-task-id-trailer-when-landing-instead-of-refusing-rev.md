---
title: "Add the `Task: <ID>` trailer when landing, instead of refusing review without it"
status: doing
priority: high
created: 2026-11-19
---

## Description

Since `TASK-346`, `Repo.edit` (`src/chitty/store.py`) refuses `-s review` when a non-`chitty:` commit on the branch lacks a `Task: <ID>` line in its last paragraph (`git.commits_missing_trailer` over `git.branch_commits`). Agents keep tripping on it: the only instruction is one line in `src/chitty/roles/work.md`, so any session that did not load that guide misses it (a human-directed session, a repair, an agent fixing a blocked ticket; seen on `TASK-403` on 2026-11-19), and the error suggests `git rebase -i`, which agent harnesses cannot run. The trailer only matters after landing, for `git log --grep <ID>` and the repair guide's search for lost work; before that, `main..task-<n>` already identifies the commits.

Decided with the owner 2026-11-19: Chitty adds the trailer itself when it lands, and the review refusal goes.

Decisions:

- Pure function `with_task_trailer(message: str, task_id: TaskId) -> str` in `src/chitty/git.py`. It returns `message` unchanged when `commits_missing_trailer([Commit("", message)], task_id)` is empty (a `chitty: ` commit, or the trailer already present). Lines and blank lines follow `commits_missing_trailer` exactly (`splitlines()`, blank means `not line.strip()`). A message that is empty or only whitespace raises `ValueError` (decided 2026-11-20: Git refuses an empty commit message unless given `--allow-empty-message`, so landing never meets one, and a one-line `Task: <ID>` message would itself count as missing its trailer, since `commits_missing_trailer` reads a one-paragraph message as having no trailer block). Otherwise, with `body = message.rstrip()`: if `body` has a blank line and its last paragraph (lines after the last blank line) consists only of lines matching `^[A-Za-z0-9-]+: .+$`, return `body + "\nTask: <ID>\n"`; else, including any one-paragraph message (which `commits_missing_trailer` reads as having no trailer block, even `Key: value`), return `body + "\n\nTask: <ID>\n"`.
- New `git.add_task_trailers(root: Path, main_branch: str, branch: str, task_id: TaskId) -> int` returns how many commits it rewrote. Callers pass the ticket worktree as `root` (in `_land_locked`, `worktree`), where `HEAD` is the ticket branch. It first raises `ChittyError` if `git rev-list --merges <main_branch>..HEAD` is not empty (cannot happen after the landing rebase). It reads `branch_commits(root, main_branch)`; if none needs a trailer it changes nothing and returns 0. Otherwise it replays every commit of `main_branch..HEAD` oldest first with `git commit-tree <tree> -p <new parent> -F -` (the message from `with_task_trailer`), keeping each commit's author name, email and date (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` and `GIT_AUTHOR_DATE` from `git show -s --format=%an%x00%ae%x00%ad --date=raw`), with the committer and committer date left to Git (the current user and time), then moves the branch with `git update-ref refs/heads/<branch> <new tip> <old tip>`. Trees do not change, so the worktree files and index stay as they are. A failing Git command raises `ChittyError` carrying its stderr, as `_git` does.
- `_land_locked` (`src/chitty/run.py`) calls it in each landing attempt, right after a successful `git.rebase_onto` and before the config and protected-path checks, so setup and the landing check run on the rewritten commits.
- Delete the trailer refusal in `Repo.edit` (the `if entering_review:` block that calls `commits_missing_trailer`). Keep `commits_missing_trailer`.
- Guides: in `src/chitty/roles/work.md`, replace the text from `ending with a` to `refuses branch commits without one.` (it wraps across lines 22 and 23) with text saying Chitty adds a `Task: <ID>` trailer to each commit when it lands the ticket, so a worker need not write one; in `tests/test_guide_work_commits.py`, replace the phrases `"Task: <ID>"` and `"refuses branch commits without one"` with phrases from the new text. In `README.md`, the sentence starting `Commits for task work should end with` says instead that `chitty run` adds a `Task: <ID>` trailer to each commit of a ticket branch when it lands it, so `git log --grep <ID>` finds the code.
- Out of scope: landings done by hand without `chitty run`.

Tests use Hypothesis (the repository tool) for the pure function, in a new `tests/test_property_task_trailer.py`; the landing test uses real Git, following `tests/test_landing.py`.

## Acceptance Criteria

- [ ] Property: messages are built from lines over the alphabet `st.characters(min_codepoint=32, max_codepoint=126)` plus `\t`, mixed with trailer-like lines (`Key: value`, unindented), blank lines, a `chitty: ` subject and a `Task: <ID>` line for `TASK-1` or `TASK-10`, joined with `\n` at drawn positions, with a first line that is not blank (filtered: `message.strip()` is not empty); the ID passed is `TASK-1`. For all of them: `commits_missing_trailer` of the result is empty; applying `with_task_trailer` twice equals once; the result equals `message` when nothing was missing, else starts with `message.rstrip()` and has exactly one more line whose `rstrip()` equals `Task: TASK-1` (count lines the same way in `message` and in the result, so `Task: TASK-1 ` with a trailing space counts as one before and two after; decided 2026-11-20). Fixed examples: `""` and `"  \n"` raise `ValueError`; `Fix\n\nSigned-off-by: A <a@example.com>` gives that plus `\nTask: TASK-1\n`; `Fix` gives `Fix\n\nTask: TASK-1\n`; `Key: value` gives `Key: value\n\nTask: TASK-1\n`. Wrong versions run against these tests, failing test recorded in a note: always appending `\n\nTask: <ID>`; never joining an existing trailer paragraph.
- [ ] A landing test with real Git: a ticket branch with three commits with distinct subjects (one with no trailer, one whose last paragraph is `Signed-off-by: A <a@example.com>`, one already ending `Task: TASK-1`) lands through `chitty run`; afterwards each commit on `main`, matched by subject, has `Task: TASK-1` exactly once among the `splitlines()` of its last paragraph, the same author and raw author date (`%ad` with `--date=raw`), and the same `^{tree}` as before landing. Direct `add_task_trailers` tests: on a branch whose commits all have the trailer it returns 0 and `HEAD` is unchanged; on a branch with a merge commit (made with `git commit-tree` on two parents and `git update-ref`, since `main` is checked out in the main checkout) it raises `ChittyError`. It fails today.
- [ ] `chitty edit TASK-1 -s review` on a branch whose commits have no trailer exits 0 and the ticket is in `review`: invert `TestReviewTrailerGate.test_review_entry_requires_trailer` in `tests/test_review_trailers.py` to assert this, dropping its stderr assertions. `make check` passes.

## Plan

Update the existing implementation and tests for the clarified requirements, restore the review cleanliness gate, verify regression failures and landing behavior, then format and run the full check.

## Notes

Suggestion origin: chitty

Blocking requirement conflict found while running the new property test. Criterion 1 requires with_task_trailer("", TASK-1) to return exactly "Task: TASK-1\n" and also requires commits_missing_trailer(result, TASK-1) to be empty. Existing commits_missing_trailer deliberately treats every one-paragraph message as missing because a trailer requires a blank-line-separated final paragraph; the requested one-line output therefore fails that assertion. The description also explicitly says a one-paragraph message has no trailer block. The planner must decide whether the empty-message example changes, or whether commits_missing_trailer semantics should accept a one-line Task trailer (which changes existing policy). I stopped before choosing or weakening the test. Focused run also found a separate test setup issue: the direct merge test tried switching to main from its linked worktree while main is checked out in the main checkout; fix that after requirements are resolved.

Planning 2026-11-20: empty messages now raise `ValueError`, and a one-paragraph message always gets a blank line before `Task:`. Resumed as `doing`, not `todo`, because the branch holds partial work and the pre-session check would send a `todo` ticket with failing work to `error` (fixed by `TASK-481`). Branch rebased onto `main`.

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
Running 867 test suites (867 total tests) across 16 workers
.................................................................................................................................................................................................................................................................................................................................................................................E.......................F.............................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp68c80qj_/repo/chitty/tasks/TASK-1--one.md actor test-agent
.......................━━━━ chitty run · 23:20:35 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
................................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
..........................F.........................................................................................F..............................................kill: 83587: No such process
.........kill: 89563: No such process
...........................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/CLAUDE.md
.....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp42o1_5e2/repo/.worktrees/task-1...
Check passed; work agent is working on TASK-1...
....TASK-1: doing → review
......../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj1sp_c1m/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy0e938yw/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkeqabmk/repo/CLAUDE.md
no next ticket for --mode work
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp6caxcxv0/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpfs3idcaq/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy6k308p8/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpzuyd3u4j/repo/CLAUDE.md
....................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
.............................landed TASK-1
landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_add_task_trailers_noop_and_merge_rejection (tests.test_landing.TestLanding.test_add_task_trailers_noop_and_merge_rejection)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_landing.py", line 112, in test_add_task_trailers_noop_and_merge_rejection
    self.git("switch", "--quiet", "main", cwd=self.worktree)
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_landing.py", line 40, in git
    result = subprocess.run(
        ["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=True
    )
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'switch', '--quiet', 'main']' returned non-zero exit status 128.

======================================================================
test_fast_forward_failure_without_main_move_is_not_retried (tests.test_landing_retry.TestLandingRetry.test_fast_forward_failure_without_main_move_is_not_retried)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_landing_retry.py", line 199, in test_fast_forward_failure_without_main_move_is_not_retried
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        self.git("rev-parse", self.branch, cwd=self.worktree).strip(), worktree_head
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: '0cb11c926dd058f00654882192fd37caaa550352' != 'd3284c76d9c318d2ce741a066118e7db20aa3c45'
- 0cb11c926dd058f00654882192fd37caaa550352
+ d3284c76d9c318d2ce741a066118e7db20aa3c45


======================================================================
test_trailer_is_added_once_and_is_detected (tests.test_property_task_trailer.TestTaskTrailer.test_trailer_is_added_once_and_is_detected)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_property_task_trailer.py", line 22, in test_trailer_is_added_once_and_is_detected
    def test_trailer_is_added_once_and_is_detected(self, source):
               ^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
    raise the_error_hypothesis_found
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_property_task_trailer.py", line 25, in test_trailer_is_added_once_and_is_detected
    self.assertEqual(commits_missing_trailer([Commit("", result)], TASK_ID), [])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: [Commit(sha='', message='Task: TASK-1\n')] != []

First list contains 1 additional elements.
First extra element 0:
Commit(sha='', message='Task: TASK-1\n')

- [Commit(sha='', message='Task: TASK-1\n')]
+ []
Failing test case: test_trailer_is_added_once_and_is_detected(
    self=<tests.test_property_task_trailer.TestTaskTrailer testMethod=test_trailer_is_added_once_and_is_detected>,
    source='',
)

======================================================================
test_dirty_branch_cannot_enter_review_until_committed (tests.test_review_merge.TestReviewMerge.test_dirty_branch_cannot_enter_review_until_committed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_review_merge.py", line 567, in test_dirty_branch_cannot_enter_review_until_committed
    rejected = self.run_cli("edit", "1", "-s", "review", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnsrcru2/repo/chitty/tasks/TASK-1--review-me.md actor test-agent


----------------------------------------------------------------------
Ran 867 tests in 115.332s

FAILED (failures=3, errors=1)
make: *** [check] Error 4

```

Criterion 1 still has a contradictory property. For the permitted message `Task: TASK-1 ` (one nonblank line with a trailing space), the specified algorithm must use `body = message.rstrip()` and return `Task: TASK-1\n\nTask: TASK-1\n`. Its split lines contain two exact `Task: TASK-1` lines, whereas the original contains zero; the criterion requires exactly one more. Please decide whether to count against the trimmed source, restrict the generated messages, or change the specified algorithm/property. This cannot be implemented and tested as written. The existing implementation and tests remain committed unchanged. The previous full check is recorded above; it failed on the now-outdated empty-message test, merge fixture, retry HEAD expectation, and inadvertent removal of the review cleanliness gate. Those failures and the requested wrong-implementation regression checks remain to be addressed after planning.

Returning to planning: criterion 1 conflicts with the required `message.rstrip()` algorithm for `Task: TASK-1 `, as detailed in the preceding note. Please resolve the property before implementation resumes; existing committed work is preserved and verification remains unfinished.

Planning 2026-11-20: criterion 1 now counts `Task: TASK-1` lines after `rstrip()` on both sides, which resolves the `Task: TASK-1 ` case. The other failures in the last check note (the outdated empty-message test, the merge fixture, the retry `HEAD` expectation, and the removed review cleanliness gate, which must stay) are implementation work against clear criteria. Resumed as `doing`.

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
Running 867 test suites (867 total tests) across 16 workers
...................................................................................................................................................................................................................................................................................................................................................................................E.......................F...........................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplpktln2g/repo/chitty/tasks/TASK-1--one.md actor test-agent
.......━━━━ chitty run · 23:24:28 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
................................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
..........................F........................................................................................F..................................................kill: 41129: No such process
...............kill: 47511: No such process
..............Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/CLAUDE.md
....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7y5gm7fc/repo/.worktrees/task-1...
Check passed; work agent is working on TASK-1...
...TASK-1: doing → review
......no next ticket for --mode work
.../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjorqljog/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprunafd5_/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpjqvba5wz/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpa432iylu/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5t_94g2l/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpuepcl6yd/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw_r2zxlx/repo/CLAUDE.md
......................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
............................landed TASK-1
landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_add_task_trailers_noop_and_merge_rejection (tests.test_landing.TestLanding.test_add_task_trailers_noop_and_merge_rejection)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_landing.py", line 112, in test_add_task_trailers_noop_and_merge_rejection
    self.git("switch", "--quiet", "main", cwd=self.worktree)
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_landing.py", line 40, in git
    result = subprocess.run(
        ["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=True
    )
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/subprocess.py", line 577, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', 'switch', '--quiet', 'main']' returned non-zero exit status 128.

======================================================================
test_fast_forward_failure_without_main_move_is_not_retried (tests.test_landing_retry.TestLandingRetry.test_fast_forward_failure_without_main_move_is_not_retried)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_landing_retry.py", line 199, in test_fast_forward_failure_without_main_move_is_not_retried
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        self.git("rev-parse", self.branch, cwd=self.worktree).strip(), worktree_head
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'ad699280d4a90fe38fa56ec3fe2cf34f125dd4ee' != 'c9d29dc7ef66fe859c45be6d1398f429f83438fd'
- ad699280d4a90fe38fa56ec3fe2cf34f125dd4ee
+ c9d29dc7ef66fe859c45be6d1398f429f83438fd


======================================================================
test_trailer_is_added_once_and_is_detected (tests.test_property_task_trailer.TestTaskTrailer.test_trailer_is_added_once_and_is_detected)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_property_task_trailer.py", line 22, in test_trailer_is_added_once_and_is_detected
    def test_trailer_is_added_once_and_is_detected(self, source):
               ^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
    raise the_error_hypothesis_found
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_property_task_trailer.py", line 25, in test_trailer_is_added_once_and_is_detected
    self.assertEqual(commits_missing_trailer([Commit("", result)], TASK_ID), [])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: [Commit(sha='', message='Task: TASK-1\n')] != []

First list contains 1 additional elements.
First extra element 0:
Commit(sha='', message='Task: TASK-1\n')

- [Commit(sha='', message='Task: TASK-1\n')]
+ []
Failing test case: test_trailer_is_added_once_and_is_detected(
    self=<tests.test_property_task_trailer.TestTaskTrailer testMethod=test_trailer_is_added_once_and_is_detected>,
    source='',
)

======================================================================
test_dirty_branch_cannot_enter_review_until_committed (tests.test_review_merge.TestReviewMerge.test_dirty_branch_cannot_enter_review_until_committed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_review_merge.py", line 567, in test_dirty_branch_cannot_enter_review_until_committed
    rejected = self.run_cli("edit", "1", "-s", "review", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-453/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpy34zog5k/repo/chitty/tasks/TASK-1--review-me.md actor test-agent


----------------------------------------------------------------------
Ran 867 tests in 85.442s

FAILED (failures=3, errors=1)
make: *** [check] Error 4

```

Regression verification: the property suite fails for an always-append mutant (including idempotence) and the fixed signed-off example fails for a mutant that never joins a trailer paragraph. Earlier check output records failures of the original empty-message and merge fixtures and the review cleanliness gate.

## History

- 2026-11-19T20:55:28Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:29Z sunny-white-dormouse: changed notes
- 2026-11-19T21:20:12Z sunny-white-dormouse: changed title, priority, description, acceptance criteria
- 2026-11-19T21:20:12Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:20:41Z sunny-white-dormouse: changed description
- 2026-11-19T21:20:41Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:22:53Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:22:53Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:22:58Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:24:34Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:24:34Z sunny-white-dormouse cold-read → todo
- 2026-11-19T23:23:20Z quick-navy-raven todo → doing
- 2026-11-19T23:24:55Z quick-navy-raven: wrote the plan
- 2026-11-19T23:51:17Z quick-navy-raven: changed owner, notes
- 2026-11-19T23:51:17Z quick-navy-raven doing → planning
- 2026-11-20T23:15:07Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:15:07Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:16:10Z quick-pearl-lapwing: changed description, acceptance criteria, notes
- 2026-11-20T23:16:10Z quick-pearl-lapwing cold-read → doing
- 2026-11-20T23:22:10Z sunny-yellow-crane: changed notes
- 2026-11-20T23:22:49Z sunny-yellow-crane: changed notes
- 2026-11-20T23:22:59Z sunny-yellow-crane: changed owner, notes
- 2026-11-20T23:22:59Z sunny-yellow-crane doing → planning
- 2026-11-20T23:24:02Z quick-pearl-lapwing: changed acceptance criteria, notes
- 2026-11-20T23:24:02Z quick-pearl-lapwing planning → doing
- 2026-11-20T23:25:44Z tidy-silver-zander: changed notes
- 2026-11-20T23:26:19Z tidy-silver-zander: wrote the plan
- 2026-11-20T23:32:46Z tidy-silver-zander: changed notes
