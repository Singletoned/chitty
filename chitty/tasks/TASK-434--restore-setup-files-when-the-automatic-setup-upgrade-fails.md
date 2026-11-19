---
title: Restore setup files when the automatic setup upgrade fails
status: planning
labels:
  - bug
priority: high
created: 2026-11-19
---

## Description

In an autocommit repository whose `chitty_version` is older than the running Chitty, the first write upgrades the setup: `Repo._prepare_write` (`src/chitty/store.py`) calls `init_repo(self.root, False)`, then commits the files it returns as `chitty: upgrade repository setup`. If anything fails in between, the setup files stay modified and uncommitted. Seen 2026-11-19 when smoke-testing 0.5.0 → 0.6.0 on a clone of echonomicon: `chitty add` failed with `project echonomicon is registered to <other path>; choose explicit project = name`, and `git status` showed ` M chitty.toml`. Cause: `init_repo` writes `chitty.toml` before `register_project` (`src/chitty/config.py`) raises. `init_repo` restores its `originals` only when its own autocommit commit fails, and `_prepare_write`'s commit has no restore at all.

Decisions:

- `init_repo` is all or nothing. It already records `originals` (`_file_state` of `chitty.toml`, `pyproject.toml`, `AGENTS.md`, `CLAUDE.md` and `.gitignore`). If anything raises after the first file is written, it restores each with `_restore_file`, removes the backlog context directories it created in this call (it `mkdir`s them; remove only those, and only when still empty), and re-raises the original exception.
- The commit moves into `init_repo`, so the restore covers it. Replace the parameter `enable_autocommit: bool` with two required parameters, `enable_autocommit: bool` and `commit_message: str | None` (no default values). When `commit_message` is not `None`, `init_repo` commits the in-repository files it wrote with that message; a failed commit restores as above. Callers:
  - `chitty init` (`src/chitty/cli.py`): `commit_message="chitty: initialize and enable autocommit"` when `--enable-autocommit` is given, else `None` (today's behaviour).
  - `Repo._prepare_write` and `Repo.refresh_setup`: `"chitty: upgrade repository setup"` (for `refresh_setup` only when `git.is_repository(self.root)`, as today); delete their own `git.commit` calls.
- Out of scope: the inbox registration under `XDG_DATA_HOME` is outside the repository and is not undone; ticket files (already restored by `_all_or_nothing`).

Tests. Hypothesis (the repository tool), in a new `tests/test_property_setup_upgrade_restore.py`, in a class inheriting `RepoTestCase` (`tests/support.py`), with real Git and real failures, no mocking. Generated state: a committed autocommit repository made by `chitty init --enable-autocommit` and then made stale by setting `chitty_version` in `chitty.toml` to `"0.1.0"` and committing; drawn variations: `AGENTS.md` absent, or with its managed block removed; `.gitignore` absent, or without `.worktrees/`; one extra context in `chitty.toml` whose backlog directory is absent or present. Drawn failure, one of: the project is already registered to another directory (`register_project(<project>, <other temp dir>)` before the write), or `.git/hooks/pre-commit` is an executable script that exits 1. Keep `max_examples` small enough that the file runs in under about 20 seconds.

## Acceptance Criteria

- [ ] Property: for every drawn state and failure, `Repo(root).add(...)` (or `chitty add` through the CLI) raises a `ChittyError` carrying the original message, and afterwards `git status --porcelain --untracked-files=all` and the bytes of `chitty.toml`, `AGENTS.md`, `CLAUDE.md` and `.gitignore` (or their absence) equal those before the write, and no backlog directory exists that did not before. It fails on `main` (the registration case leaves ` M chitty.toml`).
- [ ] With no failure, the same write commits `chitty: upgrade repository setup` and then the ticket, and leaves `git status --porcelain` empty; `chitty init --enable-autocommit` still commits `chitty: initialize and enable autocommit`, and plain `chitty init` commits nothing (existing tests in `tests/test_init_workflow.py` and `tests/test_autocommit.py` pass unchanged).
- [ ] Plausible wrong versions, each run against the property and recorded in a note with the failing case: restoring only on the registration error; restoring files but not removing created backlog directories; keeping the commit in `_prepare_write`. `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:05Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:06Z sunny-white-dormouse: changed notes
- 2026-11-19T21:06:45Z sunny-white-dormouse: changed title, labels, priority, description, acceptance criteria
- 2026-11-19T21:06:45Z sunny-white-dormouse backlog → planning
