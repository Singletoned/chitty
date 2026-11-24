---
title: Move the setup upgrade commit into `init_repo` so a failed commit is restored
status: doing
labels:
  - bug
priority: high
depends_on:
  - TASK-434
  - TASK-428
created: 2026-11-19
---

## Description

Second half of `TASK-434`, split out during planning on 2026-11-19. In an autocommit repository with an old `chitty_version`, `Repo._prepare_write` (`src/chitty/store.py`) calls `init_repo(self.root, False)` and then commits the files it returns as `chitty: upgrade repository setup`. If that commit fails (a refusing `pre-commit` hook, for example), the upgraded setup files stay changed and uncommitted. `Repo.refresh_setup` (called by `chitty run`, `src/chitty/run.py`) has the same shape. Probed on `main` at `02ece9f1` (2026-11-24), with a stale setup and a `pre-commit` hook that exits 1: both `chitty add T -d x` and `Repo.open(root).refresh_setup()` raise the hook error and leave `git status --porcelain` showing ` M .gitignore`, ` M AGENTS.md`, ` M chitty.toml` and `?? CLAUDE.md`.

`TASK-434` (done) made `init_repo` restore setup files and created directories on any failure inside its `try` block, which already includes its own `chitty: initialize and enable autocommit` commit. `TASK-428` (done) put `locks.main_checkout_lock` around `init_repo` and the setup commit in `_prepare_write`; keep that lock around the `init_repo` call.

Fix: move the commit into `init_repo` so its restore covers it.

- `init_repo(directory: Path, enable_autocommit: bool, commit_message: str | None)`: a third required parameter, no default. Inside the `try`, replace `if enable_autocommit and committed:` with `if commit_message is not None and committed:`, committing `committed` (its existing filter, `path.is_relative_to(directory) and not path.is_dir()`, only when the list is not empty) with `commit_message`. `enable_autocommit` keeps its other uses (`git.require_clean`, `_set_autocommit`); only it requires a clean tree, as today.
- `chitty init` (`src/chitty/cli.py`) passes `"chitty: initialize and enable autocommit"` with `--autocommit`, else `None`.
- `_prepare_write` passes `"chitty: upgrade repository setup"` and deletes its own file filter and `git.commit` call.
- `refresh_setup` passes `"chitty: upgrade repository setup"` only when `git.is_repository(self.root)`, else `None`, deletes its own filter and `git.commit` call, and still prints each returned path to stderr.

Out of scope: restoring the inbox registration `init_repo` writes outside the repository (`TASK-434` covers it as far as it goes); the `ManagedGuideError` warning path in `_prepare_write` (unchanged).

Tests:

- Extend the Hypothesis property `test_failure_restores_setup` in `tests/test_property_init_restore.py`. Add two members to its `case` set, which becomes `("stale", "registration")`, `("fresh", "registration")`, `("fresh", "hook")`, `("stale", "hook")` and `("refresh", "hook")`, and an `@example` for each new one (with `agents_removed`, `ignore_removed` and `extra_present` false). `("stale", "hook")` runs `chitty add T -d x`, as `stale` does today. The test branches on `kind == "stale"` in three places today; `refresh` takes the `stale` path in the first two (the project name from `self.stale(...)`, and the registration branch), so write them as `kind in ("stale", "refresh")`. In the third, the action: for `refresh`, call `Repo.open(root).refresh_setup()` inside `self.assertRaises(ChittyError)` and assert the exception text contains the expected text (`HOOKSTDERR`), instead of `CliRunner().invoke`; other kinds keep the CLI call and its exit-code and output assertions. For every case the existing assertion stands: `snapshot(root)` after equals `snapshot(root)` before (`HEAD`, `git status`, the setup files and the `chitty` directories).
- A new example test in `tests/test_cli.py` class `TestInit`: after `git init`, user name and email config and one `git commit --allow-empty -m base` in `self.root` (which already holds `chitty.toml` from `RepoTestCase`), `self.run_cli("init")` without `--autocommit` exits 0, `git rev-parse HEAD` is unchanged, and `git status --porcelain` is not empty. It passes today; it guards wrong version W2 below.

No new property for `chitty init`: its commit choice is a fixed set of two (`--autocommit` or not), each tested (the `--autocommit` commit by existing tests in `tests/test_cli.py` `TestInit` and by `("fresh", "hook")`).

Probed while planning with this recipe: the extended property fails on `main` in its new `("stale", "hook")` and `("refresh", "hook")` members (snapshot differs: setup files modified; the other three members already pass), passes with the fix, and fails against wrong version W1: `refresh_setup` passing `None` always (`ChittyError not raised`). Re-run it once against `main` and W1, and the new `TestInit` test against W2: `chitty init` passing `"chitty: initialize and enable autocommit"` whether or not `--autocommit` is given. Run against `main` with `PYTHONPATH` pointing at a copy of `main`'s `src` (or a separate checkout). Make W1 and W2 as uncommitted edits, run the test, then `git checkout -- <files>`; record the three runs in a note.

## Acceptance Criteria

- [ ] The extended `test_failure_restores_setup` passes; its `("stale", "hook")` and `("refresh", "hook")` members fail on `main`, and the test fails against W1; a note records both runs
- [ ] The new `TestInit` test passes, and fails against W2; a note records the run
- [ ] `make check` passes

## Plan

Move setup commits into init_repo; extend restoration and init tests; verify regression cases and full checks.

## Notes

Implementation is partially changed, but required regression tests and main/W1/W2 evidence remain outstanding. The ticket is clear and no external obstacle exists; status remains doing.

make check passed: 1168 tests and 620 subtests. Requested failure-on-main/W1/W2 evidence was not performed.

## History

- 2026-11-19T21:17:37Z sunny-white-dormouse → backlog
- 2026-11-19T21:17:46Z sunny-white-dormouse: changed dependencies
- 2026-11-24T07:57:04Z kind-navy-toad: changed description, acceptance criteria
- 2026-11-24T07:57:04Z kind-navy-toad backlog → planning
- 2026-11-24T07:57:23Z kind-navy-toad planning → cold-read
- 2026-11-24T07:58:07Z kind-navy-toad: changed description, acceptance criteria
- 2026-11-24T08:00:23Z kind-navy-toad: changed description
- 2026-11-24T08:00:23Z kind-navy-toad cold-read → todo
- 2026-11-24T08:41:30Z lively-hazel-kestrel todo → doing
- 2026-11-24T08:44:57Z lively-hazel-kestrel: wrote the plan
- 2026-11-24T08:48:18Z lively-hazel-kestrel: changed notes
- 2026-11-24T08:51:21Z lively-hazel-kestrel: changed notes
