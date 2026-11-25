---
title: Skip the automatic setup upgrade with a warning while setup files have uncommitted changes
status: todo
labels:
  - bug
depends_on:
  - TASK-464
created: 2026-11-24
provisional: true
---

## Description

Split from `TASK-133` (2026-11-24). In an autocommit repository with a stale `chitty_version`, the first write runs `Repo._prepare_write` (`src/chitty/store.py`), which calls `init_repo(self.root, False, "chitty: upgrade repository setup")` inside `locks.main_checkout_lock`. `init_repo` commits whole files, so an uncommitted edit someone had made to a setup file goes into that commit too. Probed on `main` at `80f6f701`: with an uncommitted line `MY UNCOMMITTED NOTE` in `AGENTS.md` and a stale setup whose upgrade rewrites `AGENTS.md`, `chitty add T -d x` makes a `chitty: upgrade repository setup` commit containing the line, and leaves `git status --porcelain` empty. `Repo.refresh_setup` already refuses in this case; `_prepare_write` does not.

Decided (planner, 2026-11-24): skip the upgrade for that write with a warning, and let the write proceed; do not refuse. This follows the person's 2026-11-23 rule (on `TASK-602`) that Chitty warns instead of refusing where it can, and the existing precedent in `_prepare_write`, which skips the upgrade with a warning when the managed guide markers are damaged (`ManagedGuideError`). The next write after the files are committed or stashed upgrades as today.

Change, in `src/chitty/store.py`:

- Move `refresh_setup`'s local `protected` tuple to a module constant `SETUP_FILES = (CONFIG_NAME, "pyproject.toml", AGENTS_FILE, ".gitignore")`, and its dirty check to a helper `_dirty_setup_files(root: Path) -> list[str]` returning, in `SETUP_FILES` order, each name for which `git.dirty_paths(root, Path(name))` is not empty. `refresh_setup` uses the helper; its behaviour and message are unchanged.
- In `_prepare_write`, inside `with locks.main_checkout_lock(self.root):` and before the `init_repo` call, when `_dirty_setup_files(self.root)` is not empty, print to stderr `warning: repository setup files have uncommitted changes: <names>; skipping repository setup upgrade until they are committed or stashed` (names joined by `, `) and return without calling `init_repo` and without reloading `self.config`, as the `ManagedGuideError` branch does (the tests do not observe the reload).

Out of scope: `chitty init` (with `--autocommit` it already requires a clean tree; without, it commits nothing); `CLAUDE.md`, which is a symlink `init_repo` manages (an uncommitted change to it can still be swept into the upgrade commit; changing it by hand is rare); linked worktrees and `autocommit = false`, which never reach the upgrade.

Test: a new `tests/test_setup_upgrade_dirty.py`, class inheriting `RepoTestCase` from `tests/support.py`. No property: the behaviour depends on which of the four setup files are dirty, a fixed set of 16 subsets, and the test covers every one (`itertools.combinations` over `SETUP_FILES` for sizes 0 to 4), each as a `subTest` in its own repository. For each subset: make a directory with `tempfile.mkdtemp(dir=self.tmp)` and `os.chdir` into it (restore the old directory with `addCleanup`); set `CHITTY_ACTOR`; `git init -b main` with user name and email; write `pyproject.toml` as `[project]\nname = "x"\n` and commit it; run `chitty init --autocommit` through `CliRunner`; set `chitty_version = "0.0.0"` in `chitty.toml` and commit. Then append `\n# local edit\n` to each file in the subset, record `git rev-list --count HEAD`, and run `chitty add T -d x` through `CliRunner`; read the warning from `result.stderr`.

- Non-empty subset: exit 0; stderr contains `uncommitted changes: <the subset's names, in SETUP_FILES order, joined by ", ">;`; the commit count grew by exactly 1 (no upgrade commit); `git status --porcelain` lists exactly the subset's files as modified, each still ending with the local edit; `chitty.toml` still contains `chitty_version = "0.0.0"`.
- Empty subset: exit 0; the count grew by 2 (`chitty: upgrade repository setup`, then the add); `git status --porcelain` is empty.

Three more cases, each in its own repository built the same way:

- Unrelated file: also commit a `NOTES.md` before `chitty init`, then change it and leave the setup files clean. `chitty add` exits 0, the count grows by 2, `NOTES.md` is not in the upgrade commit (`git show --name-only --format= HEAD~1`), and `git status --porcelain` is ` M NOTES.md`. This passes today; it guards wrong version W3 (skipping when any file in the repository is dirty).
- Untracked setup file: do not write or commit `pyproject.toml` before `chitty init`; after the stale commit, write it untracked with the same `[project]\nname = "x"\n` content (no `[tool.chitty]`). `chitty add` exits 0, the count grows by 1, `result.stderr` contains `uncommitted changes: pyproject.toml;`, and `git status --porcelain` is `?? pyproject.toml`. This fails today; it guards wrong version W4 (checking only tracked files, for example with `git diff`).
- `refresh_setup`: with `AGENTS.md` changed, `Repo.open(root).refresh_setup()` raises `ChittyError` whose text is exactly `repository setup files have uncommitted changes; commit or stash these first: AGENTS.md`. This passes today and pins the message through the refactor.

Probed while planning with this recipe: on `main` 15 of the 16 subsets fail (every non-empty one: an upgrade commit is made); with the change all pass; against wrong version W1 (checking only `AGENTS.md`) 14 fail (the 7 subsets without `AGENTS.md` upgrade, and the 7 with `AGENTS.md` and another file get a warning naming only `AGENTS.md`); against W2 (raising `ChittyError` instead of warning) 15 fail. The three extra cases were probed too: on `main` only the untracked case fails; with the change all pass. Re-run once against `main` and W1 to W4 as uncommitted edits, restore the tree, and record the results in a note.

## Acceptance Criteria

- [ ] Every case in `tests/test_setup_upgrade_dirty.py` passes; the non-empty subsets and the untracked case fail on `main`, and the test fails against each of W1 to W4; a note records the runs
- [ ] `grep -n _dirty_setup_files src/chitty/store.py` shows a call in `_prepare_write` and one in `refresh_setup`; the `refresh_setup` case passes; `make check` passes

## History

- 2026-11-24T08:42:39Z kind-navy-toad → backlog
- 2026-11-24T08:43:22Z kind-navy-toad: changed dependencies, description
- 2026-11-24T09:10:51Z kind-navy-toad: changed title, description, acceptance criteria
- 2026-11-24T09:10:51Z kind-navy-toad backlog → planning
- 2026-11-24T09:11:33Z kind-navy-toad planning → cold-read
- 2026-11-24T09:13:15Z kind-navy-toad: changed description, acceptance criteria
- 2026-11-24T09:13:15Z kind-navy-toad cold-read → planning
- 2026-11-24T09:13:40Z kind-navy-toad planning → cold-read
- 2026-11-24T09:14:56Z kind-navy-toad: changed description, acceptance criteria
- 2026-11-24T09:14:56Z kind-navy-toad cold-read → todo
