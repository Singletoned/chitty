---
title: Stop chitty init managing the Pi extension
status: error
labels:
  - needs-minor
depends_on:
  - TASK-329
parent: TASK-275
created: 2026-11-13
---

## Description

Stop `chitty init` validating, installing or updating the Pi extension, or changing Pi settings via the `exposeSessionEnvironment` migration. Never inspect or modify existing extension files, `chitty-extension.sha256`, or Pi settings; preserve local edits. Keep the bundled extension for the subsequent removal ticket. Rewrite obsolete installer and settings-migration assertions in `tests/test_cli.py`, `tests/test_next.py`, and other affected tests. Document that existing installations may still autoload and users should inspect and remove them and their state file manually, then restart Pi. Do not change runner commands or remove the bundled extension in this ticket. Use Hypothesis to vary present and absent files, arbitrary file contents, and repeated fresh and existing-project init runs. Write tests first and record their failures before the fix.

## Acceptance Criteria

- [ ] Generated tests show repeated `chitty init` never creates or changes the installed extension or state file and never changes Pi settings, including `exposeSessionEnvironment`; tests fail against the current installer and migration.
- [ ] Documentation describes manual cleanup; `make check` passes without tests requiring Chitty to manage Pi extension files or settings.

## Plan

Add Hypothesis regression coverage for repeated fresh and existing-project init runs across present/absent arbitrary extension, state, and settings files; run it before implementation and record failures. Remove init installation, validation, and Pi settings migration behavior while retaining the bundled extension. Replace obsolete assertions and document manual cleanup and restart guidance. Run make format and make check, then commit code and tests.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-321/1`. Check it against the current criteria; do not trust it.

The configuration prerequisite was completed in `c2eae4b`; the human work and review trials in `TASK-278` do not block stopping installation.

Blocked: The implementation removes Pi extension/settings handling from init and the Hypothesis regression test failed before the fix, showing extension validation, installation, and settings migration failures. After the implementation, make check still fails in legacy assertions in tests/test_cli.py and tests/test_next.py that expect init/runner setup to replace extensions; one legacy setup-failure test also expects validation to abort init. The new property test additionally hits Hypothesis’s 200 ms deadline because repeated init is slow and must configure an appropriate deadline. These are in-scope test rewrites, but need to be completed and reverified before review; no criteria are being claimed as complete.

Planner, 2026-11-14: the block note lists only in-scope work (rewriting legacy init/extension assertions in `tests/test_cli.py` and `tests/test_next.py`, and giving the Hypothesis test a suitable `deadline`), not an external obstacle, so this returns to `doing`. Continue from the existing commits on `task-321`.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
461 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 528 test suites (528 total tests) across 16 workers
.....................................................................................................F...................................F..E.........F.F..F..................................................................................................................................................................................................━━━━ chitty run · 09:25:59 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
..............F..F.....E............................................................Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5ym9iew5...
...............................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/CLAUDE.md
.....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/.worktrees/task-1...
.................................chitty 0.1.31 is out: run uv tool upgrade chitty
...................TASK-1: doing → review
.no next ticket for --mode work
.....landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_init_keeps_a_newer_pi_extension_and_finishes_setup (tests.test_cli.TestInit.test_init_keeps_a_newer_pi_extension_and_finishes_setup)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 378, in test_init_keeps_a_newer_pi_extension_and_finishes_setup
    original = extension.read_bytes()
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_abc.py", line 625, in read_bytes
    with self.open(mode='rb') as f:
         ~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5zjljzha/pi-agent/extensions/chitty.ts'

======================================================================
test_repeated_init_leaves_pi_files_byte_identical (tests.test_init_pi_isolation.TestInitPiIsolation.test_repeated_init_leaves_pi_files_byte_identical)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_init_pi_isolation.py", line 18, in test_repeated_init_leaves_pi_files_byte_identical
    extension=st.one_of(st.none(), st.binary(max_size=80)),
           ^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
    raise the_error_hypothesis_found
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1040, in test
    raise DeadlineExceeded(
        datetime.timedelta(seconds=runtime), self.settings.deadline
    )
hypothesis.errors.DeadlineExceeded: Test took 256.77ms, which exceeds the deadline of 200.00ms. If you expect test cases to take this long, you can use @settings(deadline=...) to either set a higher deadline, or to disable it with deadline=None.
Failing test case: test_repeated_init_leaves_pi_files_byte_identical(
    self=<tests.test_init_pi_isolation.TestInitPiIsolation testMethod=test_repeated_init_leaves_pi_files_byte_identical>,
    extension=None,
    state=None,
    settings=b'\x00\x00',
    existing=False,
    repeat=3,
)

======================================================================
test_init_removes_ineffective_pi_session_environment_setting (tests.test_cli.TestIdentity.test_init_removes_ineffective_pi_session_environment_setting)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 2158, in test_init_removes_ineffective_pi_session_environment_setting
    self.assertIn(f"updated {settings}", result.stdout)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/home/.pi/agent/settings.json' not found in 'updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty.toml\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty/tasks\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty/human\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty/backlog\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/data/chitty/inbox/repo\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/.gitignore\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/AGENTS.md\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/CLAUDE.md\n'

======================================================================
test_init_failure_leaves_setup_files_unchanged (tests.test_cli.TestInit.test_init_failure_leaves_setup_files_unchanged)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 405, in test_init_failure_leaves_setup_files_unchanged
    result = self.run_cli("init", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 90, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty.toml
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty/tasks
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty/human
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty/backlog
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/data/chitty/inbox/repo
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/.gitignore
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/AGENTS.md
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/CLAUDE.md


======================================================================
test_init_installs_pi_extension_from_subdirectory_and_outside_git (tests.test_cli.TestInit.test_init_installs_pi_extension_from_subdirectory_and_outside_git) (directory=PosixPath('/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkwp49a2/repo/subdirectory'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 467, in test_init_installs_pi_extension_from_subdirectory_and_outside_git
    self.assertNotEqual(extension.read_bytes(), previous_extension)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'subdirectory' == b'subdirectory'

======================================================================
test_init_installs_pi_extension_from_subdirectory_and_outside_git (tests.test_cli.TestInit.test_init_installs_pi_extension_from_subdirectory_and_outside_git) (directory=PosixPath('/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkwp49a2/outside-git'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 467, in test_init_installs_pi_extension_from_subdirectory_and_outside_git
    self.assertNotEqual(extension.read_bytes(), previous_extension)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'outside-git' == b'outside-git'

======================================================================
test_init_replaces_a_tracked_pi_extension (tests.test_cli.TestInit.test_init_replaces_a_tracked_pi_extension)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 370, in test_init_replaces_a_tracked_pi_extension
    self.assertNotEqual(extension.read_bytes(), previous_source)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'previous Chitty extension' == b'previous Chitty extension'

======================================================================
test_run_refreshes_setup_before_starting_pi (tests.test_next.TestNext.test_run_refreshes_setup_before_starting_pi)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_next.py", line 982, in test_run_refreshes_setup_before_starting_pi
    self.assertNotEqual(extension.read_text(), "old extension")
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'old extension' == 'old extension'

======================================================================
test_run_replaces_an_outdated_extension_before_starting_pi (tests.test_next.TestNext.test_run_replaces_an_outdated_extension_before_starting_pi)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_next.py", line 1043, in test_run_replaces_an_outdated_extension_before_starting_pi
    self.assertNotEqual(seen.read_bytes(), b"old extension")
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'old extension' == b'old extension'

----------------------------------------------------------------------
Ran 528 tests in 78.994s

FAILED (failures=7, errors=2)
make: *** [check] Error 9

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-321`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
461 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 528 test suites (528 total tests) across 16 workers
.....................................................................................................F...................................F..E.........F.F..F..................................................................................................................................................................................................━━━━ chitty run · 09:25:59 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
..............F..F.....E............................................................Running check in /var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5ym9iew5...
...............................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/CLAUDE.md
.....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmppvp_tzlx/repo/.worktrees/task-1...
.................................chitty 0.1.31 is out: run uv tool upgrade chitty
...................TASK-1: doing → review
.no next ticket for --mode work
.....landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_init_keeps_a_newer_pi_extension_and_finishes_setup (tests.test_cli.TestInit.test_init_keeps_a_newer_pi_extension_and_finishes_setup)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 378, in test_init_keeps_a_newer_pi_extension_and_finishes_setup
    original = extension.read_bytes()
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_abc.py", line 625, in read_bytes
    with self.open(mode='rb') as f:
         ~~~~~~~~~^^^^^^^^^^^
  File "/Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp5zjljzha/pi-agent/extensions/chitty.ts'

======================================================================
test_repeated_init_leaves_pi_files_byte_identical (tests.test_init_pi_isolation.TestInitPiIsolation.test_repeated_init_leaves_pi_files_byte_identical)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_init_pi_isolation.py", line 18, in test_repeated_init_leaves_pi_files_byte_identical
    extension=st.one_of(st.none(), st.binary(max_size=80)),
           ^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 2334, in wrapped_test
    raise the_error_hypothesis_found
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/.venv/lib/python3.13/site-packages/hypothesis/core.py", line 1040, in test
    raise DeadlineExceeded(
        datetime.timedelta(seconds=runtime), self.settings.deadline
    )
hypothesis.errors.DeadlineExceeded: Test took 256.77ms, which exceeds the deadline of 200.00ms. If you expect test cases to take this long, you can use @settings(deadline=...) to either set a higher deadline, or to disable it with deadline=None.
Failing test case: test_repeated_init_leaves_pi_files_byte_identical(
    self=<tests.test_init_pi_isolation.TestInitPiIsolation testMethod=test_repeated_init_leaves_pi_files_byte_identical>,
    extension=None,
    state=None,
    settings=b'\x00\x00',
    existing=False,
    repeat=3,
)

======================================================================
test_init_removes_ineffective_pi_session_environment_setting (tests.test_cli.TestIdentity.test_init_removes_ineffective_pi_session_environment_setting)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 2158, in test_init_removes_ineffective_pi_session_environment_setting
    self.assertIn(f"updated {settings}", result.stdout)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/home/.pi/agent/settings.json' not found in 'updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty.toml\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty/tasks\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty/human\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/chitty/backlog\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/data/chitty/inbox/repo\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/.gitignore\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/AGENTS.md\nupdated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpsg1jl7fv/repo/CLAUDE.md\n'

======================================================================
test_init_failure_leaves_setup_files_unchanged (tests.test_cli.TestInit.test_init_failure_leaves_setup_files_unchanged)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 405, in test_init_failure_leaves_setup_files_unchanged
    result = self.run_cli("init", exit_code=1)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 90, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 1 : updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty.toml
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty/tasks
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty/human
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/chitty/backlog
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/data/chitty/inbox/repo
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/.gitignore
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/AGENTS.md
updated /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpockuu_8m/repo/CLAUDE.md


======================================================================
test_init_installs_pi_extension_from_subdirectory_and_outside_git (tests.test_cli.TestInit.test_init_installs_pi_extension_from_subdirectory_and_outside_git) (directory=PosixPath('/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkwp49a2/repo/subdirectory'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 467, in test_init_installs_pi_extension_from_subdirectory_and_outside_git
    self.assertNotEqual(extension.read_bytes(), previous_extension)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'subdirectory' == b'subdirectory'

======================================================================
test_init_installs_pi_extension_from_subdirectory_and_outside_git (tests.test_cli.TestInit.test_init_installs_pi_extension_from_subdirectory_and_outside_git) (directory=PosixPath('/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpkkwp49a2/outside-git'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 467, in test_init_installs_pi_extension_from_subdirectory_and_outside_git
    self.assertNotEqual(extension.read_bytes(), previous_extension)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'outside-git' == b'outside-git'

======================================================================
test_init_replaces_a_tracked_pi_extension (tests.test_cli.TestInit.test_init_replaces_a_tracked_pi_extension)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_cli.py", line 370, in test_init_replaces_a_tracked_pi_extension
    self.assertNotEqual(extension.read_bytes(), previous_source)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'previous Chitty extension' == b'previous Chitty extension'

======================================================================
test_run_refreshes_setup_before_starting_pi (tests.test_next.TestNext.test_run_refreshes_setup_before_starting_pi)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_next.py", line 982, in test_run_refreshes_setup_before_starting_pi
    self.assertNotEqual(extension.read_text(), "old extension")
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'old extension' == 'old extension'

======================================================================
test_run_replaces_an_outdated_extension_before_starting_pi (tests.test_next.TestNext.test_run_replaces_an_outdated_extension_before_starting_pi)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-321/tests/test_next.py", line 1043, in test_run_replaces_an_outdated_extension_before_starting_pi
    self.assertNotEqual(seen.read_bytes(), b"old extension")
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'old extension' == b'old extension'

----------------------------------------------------------------------
Ran 528 tests in 78.994s

FAILED (failures=7, errors=2)
make: *** [check] Error 9

```
````

Planner, 2026-11-14: this `error` comes from the pre-session check failing on unfinished work, not from the ticket. Once TASK-329 lands, `chitty run --errors` (or a return to `doing`) will start the agent despite the failing check. The previous worker's uncommitted changes in `.worktrees/task-321` are the implementation so far.

## History

- 2026-11-13T22:24:27Z mellow-umber-lapwing → backlog
- 2026-11-13T22:24:50Z mellow-umber-lapwing: changed labels, dependencies, description, acceptance criteria
- 2026-11-13T22:24:50Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:25:23Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:25:23Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:26:25Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:26:25Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:32:40Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:32:40Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:44:31Z mellow-umber-lapwing: changed notes
- 2026-11-13T22:44:31Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:44:33Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:44:33Z mellow-umber-lapwing planning → todo
- 2026-11-13T23:23:47Z mellow-umber-lapwing: changed dependencies, notes
- 2026-11-13T23:25:37Z jolly-indigo-otter todo → doing
- 2026-11-13T23:25:50Z jolly-indigo-otter: wrote the plan
- 2026-11-13T23:28:40Z jolly-indigo-otter: changed notes
- 2026-11-13T23:28:40Z jolly-indigo-otter doing → blocked
- 2026-11-14T09:21:01Z jolly-silver-falcon: changed notes
- 2026-11-14T09:21:01Z jolly-silver-falcon blocked → doing
- 2026-11-14T09:27:05Z mellow-lilac-jay: changed notes
- 2026-11-14T09:27:05Z mellow-lilac-jay doing → error
- 2026-11-14T11:43:09Z jolly-silver-falcon: changed dependencies, notes
