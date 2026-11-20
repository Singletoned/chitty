---
title: Find ticket contexts from ref file paths, not every ref's history
status: doing
parent: TASK-376
created: 2026-11-20
---

## Description

`Repo.discovered_contexts` (`src/chitty/store.py`) returns the configured contexts, every directory under `chitty/` in the working tree, and every context directory found in any ref's history (`self._history()`, from `git.historical_files`). Every autocommitted write calls it (`Repo._commit` runs `check.fix`, whose `check.check` calls it), as do `context_of`, `chitty list` and `chitty check`. `TASK-376` removes the history scan. `Repo.ticket_ids()` (`TASK-474`) already finds the ticket files that count: the working tree's, `main`'s, and each ticket branch's own file (`_collect_ticket_ids`). This ticket takes context discovery from those paths. It is split out of `TASK-378`, which switches the ticket reads themselves.

Decisions:

- Move the part of `_collect_ticket_ids` that chooses the refs (`main`'s tip and each ticket branch whose prefix is configured) and reads their files with `git.files_at` into a helper `_ref_files() -> dict[str, list[tuple[Path, str]]]`, cached in `self._ticket_ref_files` as today (cache an empty result too: test for `None`, not truthiness) and cleared in `_invalidate`. When `git.is_repository(self.root)` is false it returns `{}` before any Git call, as `_collect_ticket_ids` does (`tests/test_check.py` builds repositories without `git init`). It validates nothing. `_collect_ticket_ids` calls it and keeps its checks and errors unchanged.
- `discovered_contexts` returns the configured contexts, then each working-tree `chitty/<dir>` directory as today, then `Context(name, "", self.root / BACKLOG_DIR / name)` for each further `<dir>` from `_ref_files()`: from `main`'s tip, every path `chitty/<dir>/<file>` or `chitty/<dir>/archive/<file>`; from a ticket branch, only such paths whose file name parses (`ids.parse_filename`) to that branch's own ID. Names that do not parse are skipped, never raised: discovery validates no file name and parses no ticket content, and does not call `ticket_ids()` or `_files`. It no longer calls `_history()`. So a conflicted ticket, a malformed ticket body or a stray file cannot make it fail, and `chitty check` keeps reporting a stray file with every other problem (`test_reports_every_problem` in `tests/test_check.py`, decided 2026-11-20 after a worker found that routing discovery through `ticket_ids()` made it raise). Reads that call `_files` keep raising on stray files as today, including `check.check`'s reference lookups (`repo.lookup`), which `test_reports_every_problem`'s fixture does not reach; that is out of scope (`TASK-378` replaces them with `Repo.exists`). The only error left on the discovery path is Git's own, such as `git.files_at` reporting a missing blob.
- Visible change: a directory that exists only on a branch that is neither `main` nor the ticket branch of the file's own ID is no longer discovered. That includes a branch named for a ticket whose prefix no configured context has (for example `other-1`): `_collect_ticket_ids` counts only branches whose prefix is configured, and that is intended. Archived paths (`chitty/<dir>/archive/...`) are included, since `_collect_ticket_ids` counts them.
- Migrate, without deleting it: `test_finds_directory_that_exists_only_in_branch_history` in `tests/test_unconfigured_directories.py` becomes `test_ignores_directory_that_exists_only_on_an_unrelated_branch`, keeping its fixture (branch `ticket` is not a ticket branch), and asserts that `chitty show OTHER-1` exits 1 with `no context` in its output (through `context_of`, which no longer finds a context for prefix `OTHER` and raises `OTHER-1: no context in ... has prefix 'OTHER'`). Migrate any other test that `make check` shows relying on a history-only directory the same way, without weakening it, and name it in the review note.
- Unchanged: `_tasks_in_location`, `lookup` and `context_of`, which `TASK-378` switches, and `_history()`, which they still use.

Tests: real Git, in a new `tests/test_discovered_contexts.py` with a class inheriting `CliTestCase` from `tests/test_cli.py` (which inherits `RepoTestCase`, so the inbox is isolated), set up with `git init -b main` and a first commit of `chitty.toml` as `tests/test_unconfigured_directories.py` does. The configured context is `tasks` with prefix `TASK`. Each case calls `Repo.open(self.root).discovered_contexts()` from the main checkout on `main` and compares the set of context names:

- `main` only: commit `chitty/other/TASK-3--x.md` on `main`, then remove the whole `chitty/other` directory from the working tree with `shutil.rmtree`, without committing, so only `main's tip has it; `other` is discovered.
- Ticket branch, own file: on branch `task-5` from `main`, commit `chitty/fifth/TASK-5--x.md`, switch back to `main`; `fifth` is discovered.
- Ticket branch, another ticket's file: on branch `task-6`, commit `chitty/sixth/TASK-9--y.md`, switch back; `sixth` is not discovered.
- Unrelated branch: on branch `feature`, commit `chitty/feat/TASK-7--z.md`, switch back; `feat` is not discovered.
- Criterion 2: the conflict and malformed fixture as stated there, with `other` from `chitty/other/TASK-3--x.md` committed on `main`.

No property: a fixed set of placements, each listed; `TASK-393` adds the generated property over placements.

## Acceptance Criteria

- [ ] Tests in a new `tests/test_discovered_contexts.py` pass: a context directory only in `main`'s tip and one holding only a ticket branch's own file are discovered (guards that pass before the change too), while a directory holding only another ticket's file on a ticket branch, or only a file on branch `feature`, is not (fails before the change)
- [ ] With `TASK-1` edited on both `task-1` and `main` since they split, a file whose body does not start with `---` committed as `TASK-2` on `main`, and `git.historical_files` patched with `unittest.mock.patch.object` to raise, `Repo.open(root).discovered_contexts()` returns the configured contexts and `other` without raising (fails on `main` before this branch, by the patched error; the conflicted and malformed tickets are guards that discovery reads no ticket content)
- [ ] The migrated test in `tests/test_unconfigured_directories.py` passes and asserts the new behaviour, and `make check` passes

## Plan

Extract cached ref file selection, use it directly for non-validating context discovery, preserve ticket ID validation, and run the existing regression tests and full checks.

## Notes

Before the fix, the discovery tests fail on the historical_files patch and the two unrelated placements; both positive guards pass. The migrated CLI test also fails because show succeeds.

The prescribed implementation makes `tests.test_check.TestCheck.test_reports_every_problem` error: `check.check` calls `discovered_contexts`, which now calls `ticket_paths` and `_files`, so `stray.txt` raises before the check can report that filename alongside the other four problems. This existing check-level behavior contradicts the proposed unconditional filename exception and the requirement that `make check` pass; the failing test is not a history-only directory test and changing it would weaken its aggregation assertion. Planning must decide whether check should retain aggregated diagnostics and specify how discovery handles invalid filenames in that path, or explicitly change the check contract and its test. The implementation and regression tests are preserved in commit `a60c5c9d`; focused tests pass, but `make check` fails on this test. `chitty fix` and formatting ran; other reported ticket warnings were pre-existing.

Planning 2026-11-20: discovery no longer goes through `ticket_ids()`; see the `_ref_files` decision. Keep the implementation in `a60c5c9d` and adapt it: drop `ticket_paths()` if nothing else needs it.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
680 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 868 test suites (868 total tests) across 16 workers
..............................................E.........................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprcwv_v9z/repo/chitty/tasks/TASK-1--one.md actor test-agent
.........━━━━ chitty run · 23:05:46 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
................................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
......................................................................................................................................................................kill: 65347: No such process
..........................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
..kill: 71121: No such process
........./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/CLAUDE.md
....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/.worktrees/task-1...
Check passed; work agent is working on TASK-1...
...TASK-1: doing → review
......no next ticket for --mode work
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/CLAUDE.md
..................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-2
landed TASK-1
landed TASK-1

======================================================================
test_reports_every_problem (tests.test_check.TestCheck.test_reports_every_problem)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/tests/test_check.py", line 37, in test_reports_every_problem
    problems = "\n".join(self.problems())
                         ~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/tests/test_check.py", line 11, in problems
    return [str(p) for p in check(self.repo, contexts, list(paths))]
                            ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/check.py", line 161, in check
    for context in repo.discovered_contexts():
                   ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 301, in discovered_contexts
    for name in sorted({path.parts[1] for path in self.ticket_paths()}):
                                                  ~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 533, in ticket_paths
    self.ticket_ids()
    ~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 529, in ticket_ids
    self._ticket_ids = self._collect_ticket_ids()
                       ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 545, in _collect_ticket_ids
    for path in self._files(context, archived):
                ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 1190, in _files
    raise ChittyError(f"{path}: {problem}")
chitty.errors.ChittyError: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp609n3sxq/repo/chitty/tasks/stray.txt: task filename 'stray.txt' must end with .md

----------------------------------------------------------------------
Ran 868 tests in 65.308s

FAILED (errors=1)
make: *** [check] Error 1

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-479`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
680 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 868 test suites (868 total tests) across 16 workers
..............................................E.........................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmprcwv_v9z/repo/chitty/tasks/TASK-1--one.md actor test-agent
.........━━━━ chitty run · 23:05:46 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
................................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
......................................................................................................................................................................kill: 65347: No such process
..........................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
..kill: 71121: No such process
........./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/CLAUDE.md
....Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpr0ehh0on/repo/.worktrees/task-1...
Check passed; work agent is working on TASK-1...
...TASK-1: doing → review
......no next ticket for --mode work
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8_dpx2b9/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8o7nfwhj/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpz3f7bmsx/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplz1cy2o3/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp7634yymz/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8tkcczdt/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpmopwfmap/repo/CLAUDE.md
..................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-2
landed TASK-1
landed TASK-1

======================================================================
test_reports_every_problem (tests.test_check.TestCheck.test_reports_every_problem)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/tests/test_check.py", line 37, in test_reports_every_problem
    problems = "\n".join(self.problems())
                         ~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/tests/test_check.py", line 11, in problems
    return [str(p) for p in check(self.repo, contexts, list(paths))]
                            ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/check.py", line 161, in check
    for context in repo.discovered_contexts():
                   ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 301, in discovered_contexts
    for name in sorted({path.parts[1] for path in self.ticket_paths()}):
                                                  ~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 533, in ticket_paths
    self.ticket_ids()
    ~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 529, in ticket_ids
    self._ticket_ids = self._collect_ticket_ids()
                       ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 545, in _collect_ticket_ids
    for path in self._files(context, archived):
                ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 1190, in _files
    raise ChittyError(f"{path}: {problem}")
chitty.errors.ChittyError: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp609n3sxq/repo/chitty/tasks/stray.txt: task filename 'stray.txt' must end with .md

----------------------------------------------------------------------
Ran 868 tests in 65.308s

FAILED (errors=1)
make: *** [check] Error 1

```
````

Moved `error` to `doing` 2026-11-20: the failing pre-session check is the earlier implementation in `a60c5c9d` (discovery through `ticket_ids()` raises on `stray.txt` in `test_reports_every_problem`). The ticket was re-planned for exactly that; adapt the code to the `_ref_files` decision.

Check failed before this session: check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
680 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 868 test suites (868 total tests) across 16 workers
.............................................E..........................................................................................................................................................................................................................................................................................................................................................................................................................................updated TASK-1 /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpw96jflgh/repo/chitty/tasks/TASK-1--one.md actor test-agent
.........━━━━ chitty run · 23:09:01 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
................................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
......................................................................................................................................................................kill: 67980: No such process
..........................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
kill: 73859: No such process
........./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/CLAUDE.md
......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpffymsqin/repo/.worktrees/task-1...
Check passed; work agent is working on TASK-1...
...TASK-1: doing → review
...no next ticket for --mode work
..../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpbnomsrtv/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmplywa9c4i/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp1yqiuovd/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpxht326ja/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwhi5yj7w/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp8bf1c5ca/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpd21f3jts/repo/CLAUDE.md
...................................................................................chitty 0.1.31 is out: run uv tool upgrade chitty
...............................landed TASK-1
landed TASK-1
landed TASK-1
landed TASK-2

======================================================================
test_reports_every_problem (tests.test_check.TestCheck.test_reports_every_problem)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/tests/test_check.py", line 37, in test_reports_every_problem
    problems = "\n".join(self.problems())
                         ~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/tests/test_check.py", line 11, in problems
    return [str(p) for p in check(self.repo, contexts, list(paths))]
                            ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/check.py", line 161, in check
    for context in repo.discovered_contexts():
                   ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 301, in discovered_contexts
    for name in sorted({path.parts[1] for path in self.ticket_paths()}):
                                                  ~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 533, in ticket_paths
    self.ticket_ids()
    ~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 529, in ticket_ids
    self._ticket_ids = self._collect_ticket_ids()
                       ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 545, in _collect_ticket_ids
    for path in self._files(context, archived):
                ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-479/src/chitty/store.py", line 1190, in _files
    raise ChittyError(f"{path}: {problem}")
chitty.errors.ChittyError: /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp2v6f6xxs/repo/chitty/tasks/stray.txt: task filename 'stray.txt' must end with .md

----------------------------------------------------------------------
Ran 868 tests in 64.789s

FAILED (errors=1)
make: *** [check] Error 1

```

## Summary

Context discovery now uses cached selected ref files without validating ticket content or working-tree filenames. The earlier regression tests failed before the original fix as recorded in the notes; focused tests and make check now pass, including the stray-file aggregation test. No additional history-only tests needed migration. Follow-up ticket TASK-378 covers remaining historical reads.

## History

- 2026-11-20T22:56:54Z quick-pearl-lapwing → planning
- 2026-11-20T22:57:07Z quick-pearl-lapwing: changed description
- 2026-11-20T22:57:07Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:58:02Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T22:58:02Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T22:58:16Z sunny-silver-yellowhammer todo → doing
- 2026-11-20T22:59:38Z sunny-silver-yellowhammer: wrote the plan
- 2026-11-20T23:00:22Z sunny-silver-yellowhammer: changed notes
- 2026-11-20T23:02:13Z sunny-silver-yellowhammer: changed owner, notes
- 2026-11-20T23:02:13Z sunny-silver-yellowhammer doing → planning
- 2026-11-20T23:03:23Z quick-pearl-lapwing: changed description, notes
- 2026-11-20T23:03:23Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:04:35Z quick-pearl-lapwing: changed title, description, acceptance criteria
- 2026-11-20T23:04:35Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T23:05:26Z quick-jade-stoat todo → doing
- 2026-11-20T23:06:39Z quick-jade-stoat: changed notes
- 2026-11-20T23:06:39Z quick-jade-stoat doing → error
- 2026-11-20T23:08:18Z quick-pearl-lapwing: changed notes
- 2026-11-20T23:08:18Z quick-pearl-lapwing error → doing
- 2026-11-20T23:09:54Z vivid-yellow-adder: changed notes
- 2026-11-20T23:10:14Z vivid-yellow-adder: wrote the plan
- 2026-11-20T23:12:24Z vivid-yellow-adder: changed summary
