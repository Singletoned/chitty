---
title: Stop `git._read_blobs` hanging on a few thousand objects
status: error
labels:
  - bug
parent: TASK-376
created: 2026-11-18
---

## Description

`_read_blobs` in `src/chitty/git.py` writes every object ID to `git cat-file --batch` and closes its input before reading any output. Once both the object list and the output exceed the pipe buffers, `cat-file` blocks writing, Chitty blocks writing its input, and both wait forever. Cold reads on 2026-11-18 reproduced it on macOS (16 KB pipes; Linux has 64 KB): about 2,900 objects of 10-byte files hung, and 2,000 objects of 1 KB files; a `process.communicate` prototype read 5,000 1 KB objects in about 2 s. Today it is reached through `historical_files`; `TASK-378` keeps it for reading ticket files from ref tips, so every read in a repository with a few thousand tickets could hang.

Decisions:

- Feed the input without blocking the output: `process.communicate(input)` and parse the returned bytes, or write the input from a thread while reading. Keep the function's signature and results, including skipping `missing` objects and the `ChittyError`s for a bad header or a non-blob.
- Decode contents as today.

Tests: in `tests/test_git.py`, inheriting `RepoTestCase`, a repository with 5000 committed files of about 1 KB each (about 5 MB of output, well past any default pipe size), read through `_read_blobs` in one call in a subprocess (`sys.executable -c ...` with `timeout=20`), so a hang fails rather than stalls the suite. The test asserts that `chitty.git.__file__` lies under this checkout's `src`, so it tests this code, and compares every returned content with the file written. No property: the bug is a size threshold, shown by one large case; the existing tests cover the parsing.

## Acceptance Criteria

- [x] `_read_blobs` returns all 5000 objects of the large case, each with the content written, within the 20 s timeout; the test fails (times out) before the change
- [ ] The existing `tests/test_git.py` tests pass unchanged, and `make check` passes

## Plan

Add a RepoTestCase regression test that creates and commits 5,000 approximately 1 KB files, invokes this checkout’s chitty.git._read_blobs in a subprocess with a 20-second timeout, and verifies every returned object and content. Run it against the current implementation to confirm the hang. Replace the sequential blocking pipe writes/reads in _read_blobs with subprocess.communicate(input=...), then parse its returned stdout using the existing cat-file batch framing and preserve missing-object, malformed-header, non-blob, decoding, and Git-failure behavior. Run the focused test, formatting, and make check; commit implementation and test with a Task: TASK-395 trailer, record verification, then set the ticket to review.

## Notes

The 5,000-object regression test timed out at 20 seconds against the original implementation, then passed after the communicate-based fix. Focused tests passed. make check reached all 653 tests but failed twice on the unrelated existing Hypothesis test test_refused_edit_restores_repository, with generated note 0 newline = triggering a TaskError message mismatch; ruff and pyright passed.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
571 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 653 test suites (653 total tests) across 16 workers
...........................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 22:42:27 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
......................................./Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
.................................F.................................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
....../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/CLAUDE.md
.......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/.worktrees/task-1...
..TASK-1: doing → review
.no next ticket for --mode work
......../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/CLAUDE.md
.............................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_refused_edit_restores_repository (tests.test_property_refused_write.TestRefusedEditProperty.test_refused_edit_restores_repository)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 313, in with_section
    candidate = self._insert_section(name, lines)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 489, in _insert_section
    return self._rebuild(preamble=preamble, sections=sections)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 503, in _rebuild
    return parse(draft.render())
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 524, in parse
    preamble, sections = _split_sections(lines[close + 1 :], first_line=close + 2)
                         ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 652, in _split_sections
    raise TaskError(f"line {number}: setext headings are not allowed; use '##' sections")
chitty.model.TaskError: line 16: setext headings are not allowed; use '##' sections

The above exception was the direct cause of the following exception:

chitty.model.TaskError: Notes text changed section boundaries; use ### for headings and close code fences

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/tests/test_property_refused_write.py", line 80, in test_refused_edit_restores_repository
    @given(

  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
    raise the_error_hypothesis_found
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/tests/test_property_refused_write.py", line 95, in test_refused_edit_restores_repository
    with self.assertRaisesRegex(ChittyError, "cannot finalize task write"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: "cannot finalize task write" does not match "Notes text changed section boundaries; use ### for headings and close code fences"
Failing test case: test_refused_edit_restores_repository(
    self=<tests.test_property_refused_write.TestRefusedEditProperty testMethod=test_refused_edit_restores_repository>,
    invalid='self-dependency',
    note='0\n=',
    title=None,
)

----------------------------------------------------------------------
Ran 653 tests in 25.031s

FAILED (failures=1)
make: *** [check] Error 1

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-395`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
571 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 653 test suites (653 total tests) across 16 workers
...........................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 22:42:27 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
......................................./Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
.................................F.................................................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
....../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/CLAUDE.md
.......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_kb2s_1x/repo/.worktrees/task-1...
..TASK-1: doing → review
.no next ticket for --mode work
......../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpysh8rho6/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwj430iro/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd35ukw2n/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpyl84yz8w/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmcfhms1t/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpq1oon83q/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp_6ydbvit/repo/CLAUDE.md
.............................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_refused_edit_restores_repository (tests.test_property_refused_write.TestRefusedEditProperty.test_refused_edit_restores_repository)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 313, in with_section
    candidate = self._insert_section(name, lines)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 489, in _insert_section
    return self._rebuild(preamble=preamble, sections=sections)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 503, in _rebuild
    return parse(draft.render())
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 524, in parse
    preamble, sections = _split_sections(lines[close + 1 :], first_line=close + 2)
                         ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/src/chitty/model.py", line 652, in _split_sections
    raise TaskError(f"line {number}: setext headings are not allowed; use '##' sections")
chitty.model.TaskError: line 16: setext headings are not allowed; use '##' sections

The above exception was the direct cause of the following exception:

chitty.model.TaskError: Notes text changed section boundaries; use ### for headings and close code fences

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/tests/test_property_refused_write.py", line 80, in test_refused_edit_restores_repository
    @given(

  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
    raise the_error_hypothesis_found
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-395/tests/test_property_refused_write.py", line 95, in test_refused_edit_restores_repository
    with self.assertRaisesRegex(ChittyError, "cannot finalize task write"):
         ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: "cannot finalize task write" does not match "Notes text changed section boundaries; use ### for headings and close code fences"
Failing test case: test_refused_edit_restores_repository(
    self=<tests.test_property_refused_write.TestRefusedEditProperty testMethod=test_refused_edit_restores_repository>,
    invalid='self-dependency',
    note='0\n=',
    title=None,
)

----------------------------------------------------------------------
Ran 653 tests in 25.031s

FAILED (failures=1)
make: *** [check] Error 1

```
````

## Summary

Implemented communicate-based Git cat-file batching and added a subprocess regression test covering 5,000 committed 1 KB blobs. The regression timed out before the fix and passes after it; all tests in tests/test_git.py pass. make check was attempted twice and failed both times in unrelated tests/test_property_refused_write.py::TestRefusedEditProperty.test_refused_edit_restores_repository. Ruff formatting/check and pyright pass. Commit: 8f416fbd (Task: TASK-395). Reviewer: assess the unrelated full-check failure; no follow-up implementation needed.

## History

- 2026-11-18T16:38:07Z lively-quartz-crane → backlog
- 2026-11-18T16:39:31Z lively-quartz-crane: changed title, labels, description, acceptance criteria
- 2026-11-18T16:39:31Z lively-quartz-crane backlog → planning
- 2026-11-18T16:40:46Z lively-quartz-crane planning → cold-read
- 2026-11-18T17:45:09Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-18T17:45:09Z lively-quartz-crane cold-read → planning
- 2026-11-18T17:45:11Z lively-quartz-crane planning → todo
- 2026-11-18T22:37:28Z zesty-russet-raven todo → doing
- 2026-11-18T22:38:30Z zesty-russet-raven: wrote the plan
- 2026-11-18T22:42:00Z zesty-russet-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-18T22:42:00Z zesty-russet-raven doing → review
- 2026-11-18T22:42:47Z quick-yellow-dormouse: changed notes
- 2026-11-18T22:42:47Z quick-yellow-dormouse review → error
