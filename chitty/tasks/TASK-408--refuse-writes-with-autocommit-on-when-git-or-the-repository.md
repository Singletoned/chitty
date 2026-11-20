---
title: Refuse writes with `autocommit` on when `git` or the repository is missing
status: review
depends_on:
  - TASK-410
created: 2026-11-19
---

## Description

With `autocommit = true`, every write commits, so Git is required. Today Chitty only finds out after writing: outside a Git work tree, `chitty add` writes the ticket file and then fails with `` `git ls-files -- ...` failed ``; with `git` missing from `PATH` and no `.git`, it writes the file and then dies with a `FileNotFoundError` traceback. Both leave an uncommitted ticket behind. (With `git` missing and a `.git` present, `git.is_repository` already raises before the write, since `TASK-405`.)

Check before writing, in `Repo._prepare_write` (`src/chitty/store.py`), which every `Repo` write method calls before changing a file, as do `chitty fix` (`src/chitty/check.py`) and `chitty import` (`src/chitty/import_backlog.py`). Put the check immediately after `self._check_setup_version()`, before the `chitty_version` early return, the linked-worktree return and the setup upgrade:

- `autocommit` is `false`: do nothing new. Chitty without Git is supported and behaves like `autocommit = false`.
- `autocommit` is `true` and `shutil.which("git")` is `None`: raise `ChittyError` naming `autocommit`, saying `git` was not found on `PATH`, and to install Git or set `autocommit = false`. This is checked first, so it wins when a `.git` exists.
- `autocommit` is `true` and `git.is_repository(self.root)` is `False`: raise `ChittyError` naming `autocommit`, naming `self.root` as not in a Git work tree, and to run `git init` or set `autocommit = false`.

Reads are unchanged. With `git` missing and no repository, commands other than `add` crash today; `TASK-410`, which this depends on, fixes that. Out of scope: `chitty init --autocommit` (it changes no files when it fails, and has its own ticket) and `chitty run`'s `refresh_setup`, since `chitty run` needs Git for its worktrees.

Tests go in a new `tests/test_autocommit_requires_git.py`, classes inheriting `RepoTestCase`. Make `git` missing with `unittest.mock.patch.dict(os.environ, {"PATH": <empty directory>})` or `CliRunner().invoke(..., env=...)`, which patch the environment, not our code (as `tests/test_git.py` does). Several test files set `autocommit = true` (`git grep -l "autocommit = true" tests`); any that write without `git init` now fail and must create the repository.

No property: the behaviour is a small fixed set of states, every one listed in criterion 1 and tested.

## Acceptance Criteria

- [ ] Grid test in `tests/test_autocommit_requires_git.py`: each of `chitty add`, `chitty edit <ID> -s planning` and `chitty note <ID> x` in every combination of `autocommit` on or off, `git` on `PATH` or not, and `git init` run or not (24 cases), each as a `subTest` building a fresh root in its own temporary directory. The `<ID>` ticket is made first, with `autocommit = false`, `git` on `PATH` and before any `git init`; `git init` then sets repository-local `user.email` and `user.name` as `tests/test_autocommit.py` does. Rows without `git init` first assert `git.is_repository(root)` is `False`, so an enclosing checkout fails loudly. Succeeds: `autocommit` off without `git init`, with or without `git`; off with `git init` and `git`; on with `git init` and `git`, where `git log -1 --format=%s` starts `chitty:` and the paths that latest commit changes include the `<ID>` ticket file (the new file for `add`). Off with `git init` but no `git`: the existing `TASK-405` error, containing `` `git` is unavailable on PATH `` (`src/chitty/git.py`). On without `git`: a message naming `autocommit` and `PATH`. On with `git` but no `git init`: a message naming `autocommit` and `git init`. Every failing case exits non-zero without a traceback and leaves every file under the root outside `.git` unchanged.
- [ ] Further tests, `autocommit` on, no `git init`, `git` on `PATH`: `chitty move <ID> human` and `chitty fix` (with nothing to fix) refuse with the criterion 1 message naming `autocommit` and `git init` and change no file; `chitty show <ID>` and `chitty list` succeed; with `chitty_version = "0.0.1"` in `chitty.toml`, `chitty add` refuses with the `git init` message and no setup file (`.gitignore`, `AGENTS.md`, `CLAUDE.md`, `chitty.toml`) changes.
- [ ] Evidence, recorded in a note. In a scratch copy of the branch, write `git show main:src/chitty/store.py` over `src/chitty/store.py` and run each case of criteria 1 and 2 on its own: every row whose expected message names `autocommit` (including the criterion 2 refusals) fails there (it exits 0 without refusing, changes files, shows a traceback, or gives a message not naming `autocommit`). The `autocommit`-off, no-`git`, `git init` rows (the `TASK-405` error) and the criterion 2 `chitty show` and `chitty list` rows are guards that pass there too; the note says so.
- [ ] `make check` passes, with any existing test that enabled `autocommit` without a repository fixed to create one.

## Plan

Strengthen the existing grid assertions and isolate additional cases, then run each against a scratch main-store baseline and the fixed branch. Run fix, format and checks, commit and hand off.

## Notes

Blocked: TASK-410, a declared dependency, is not present on this branch/main, so no-git command behavior outside add cannot be verified as specified. The current implementation and two focused tests are present, and make check passed, but the required 24-case grid, additional move/fix/read/stale-setup tests, and main-baseline evidence remain incomplete. The dependency owner must land TASK-410; then resume and complete these criteria.

Unblocked 2026-11-19 by a planning session: `TASK-410` landed on `main` at 11:31 (`7b9b5a4a`), and this branch already contains it (`git merge-base --is-ancestor 7b9b5a4a task-408` succeeds; `tests/test_no_git_installed.py` is here). `chitty` still lists `TASK-410` as `error` because the `task-413` branch carries an older copy with a newer commit time, which `TASK-378` fixes; that clears when `task-413` lands. The missing work is this ticket's own: the 24-case grid, the move, fix, read and stale-setup tests, and the evidence from `main`.

Verified the refusal matrix: tests/test_autocommit_requires_git.py passes all 24 grid combinations plus move/fix/read and stale-setup checks. `make check` passes (712 tests). The requested unfixed-main baseline run was not performed; do not treat criterion 3 as demonstrated until review verifies it.

Review failed (design): Criterion 3 requires every refusing row to fail on main, but criterion 1 explicitly requires the existing TASK-405 PATH error for autocommit off, initialized, git missing; those three rows already pass on main. Decide which rows must regress and revise criterion 3. All findings below are newly discovered; the prior note already disclosed that baseline evidence was missing.
1: fail - The grid passes in make check, but it never asserts that errors name autocommit or that the resulting commit contains the ticket file. Add those assertions; main baseline grid printed six failures for autocommit on without a repository, but the initialized no-git rows passed because the autocommit assertion is absent.
2: fail - make check passes the combined test, but the main baseline run stopped at move with missing git init message, so it did not demonstrate that fix and stale-setup assertions fail without the change. Isolate the cases and record baseline evidence for each.
3: fail - Baseline using main store.py with the branch tests printed six grid failures and one combined-test failure, not failures for every refusing row. Existing off/initialized/no-git behavior is deliberately unchanged, so this criterion cannot be met as written.
4: pass - make check printed Ran 720 tests and OK; ruff and pyright passed.

Planning 2026-11-20: criterion 3 reworded for the review's design finding (the `TASK-405` rows cannot fail on `main`). The review's other findings are implementation gaps against clear criteria: the grid must assert that refusals name `autocommit` and that the commit holds the ticket file (criterion 1), and the criterion 2 cases need separate baseline runs. Branch rebased onto `main` (old tip tagged `task-408-before-rebase`).

Regression evidence: copied src and tests into tmp/task-408-baseline, replaced store.py with git show main:src/chitty/store.py, and ran each of the 24 grid cases separately using a scratch-only subtest selector. All nine autocommit-on refusal rows failed; all other rows passed, including the three autocommit-off initialized/no-git TASK-405 guards. Separate move, fix and stale-setup refusal tests failed; show and list passed. The fixed branch passes all six focused tests.

## Summary

Autocommit writes now check Git availability and repository membership before changing files. The 24-case grid verifies errors, unchanged files and committed ticket paths; independent move, fix, stale-setup and read tests cover the remaining cases. Each regression was checked against main store.py in a scratch copy; make check passed (858 tests). No follow-ups.

## History

- 2026-11-19T09:06:20Z lively-quartz-crane → planning
- 2026-11-19T09:06:59Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T09:06:59Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:10:33Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T09:10:33Z lively-quartz-crane cold-read → planning
- 2026-11-19T09:10:53Z lively-quartz-crane planning → cold-read
- 2026-11-19T09:14:28Z lively-quartz-crane: changed dependencies, description, acceptance criteria
- 2026-11-19T09:21:32Z lively-quartz-crane cold-read → todo
- 2026-11-19T11:42:06Z sunny-ochre-raven todo → doing
- 2026-11-19T11:42:57Z sunny-ochre-raven: wrote the plan
- 2026-11-19T11:45:27Z sunny-ochre-raven: changed notes
- 2026-11-19T11:45:27Z sunny-ochre-raven doing → blocked
- 2026-11-19T12:47:56Z quick-ginger-lapwing: changed notes
- 2026-11-19T12:47:56Z quick-ginger-lapwing blocked → doing
- 2026-11-19T12:53:22Z open-coral-marten: changed notes, summary
- 2026-11-19T12:53:22Z open-coral-marten doing → review
- 2026-11-19T13:36:58Z nimble-ebony-zander: changed owner, acceptance criteria, notes
- 2026-11-19T13:36:58Z nimble-ebony-zander review → planning
- 2026-11-20T22:36:15Z quick-pearl-lapwing: changed acceptance criteria, notes
- 2026-11-20T22:36:15Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:37:15Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-20T22:37:15Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T22:43:06Z mellow-ochre-stoat todo → doing
- 2026-11-20T22:44:25Z mellow-ochre-stoat: wrote the plan
- 2026-11-20T22:46:06Z mellow-ochre-stoat: changed notes
- 2026-11-20T22:47:22Z mellow-ochre-stoat: changed summary
- 2026-11-20T22:47:25Z mellow-ochre-stoat doing → review
