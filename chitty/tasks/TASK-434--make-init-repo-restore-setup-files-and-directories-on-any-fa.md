---
title: Make `init_repo` restore setup files and directories on any failure
status: todo
labels:
  - bug
priority: high
created: 2026-11-19
---

## Description

`init_repo` (`src/chitty/store.py`) upgrades or creates a repository's setup, and is not all or nothing: a failure part way leaves setup files changed. Reproduced on `main` 2026-11-19 (first seen smoke-testing 0.5.0 → 0.6.0 on a clone of echonomicon): in an autocommit repository whose `chitty_version` is old, `chitty add` runs the upgrade through `Repo._prepare_write`, `init_repo` writes `chitty.toml`, then `register_project` (`src/chitty/config.py`) raises `project <name> is registered to <path>; choose explicit project = name`, and `git status` shows ` M chitty.toml`. `init_repo` restores its `originals` only when its own `--autocommit` commit fails, and even then leaves a `chitty/` directory it created.

The upgrade commit that `_prepare_write` makes after `init_repo` returns is out of scope here: `TASK-464` moves it into `init_repo`.

Decisions:

- Wrap everything in `init_repo` from the first write to disk through its own commit in one `try`, with `except BaseException:` that restores and re-raises the original exception (replacing today's `except ChittyError` around the commit).
- Restore means: each path in `originals` (`chitty.toml`, `pyproject.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`) goes back to its `_file_state` with `_restore_file`; and every directory this call created is removed. `init_repo` creates backlog context directories with `mkdir(parents=True)`, so record each directory, parents included, that did not exist before, and remove them deepest first, only when empty.
- `init_repo` computes `originals` twice; keep only the second (both precede any write).
- Out of scope: the inbox registration under `XDG_DATA_HOME` (outside the repository) is not undone; `pyproject.toml` (`[tool.chitty]`) setups are not drawn by the test.

Tests. Hypothesis (the repository tool), in a new `tests/test_property_init_restore.py`, in a class inheriting `RepoTestCase` (`tests/support.py`), with real Git and real failures, no mocking of files.

- Each example builds its own state: a fresh directory from `tempfile.mkdtemp(dir=self.tmp)` as the repository, and a fresh data directory set as `XDG_DATA_HOME` with `mock.patch.dict(os.environ, ...)` for that example only, so registrations never carry over between examples. It runs `git init`, sets `user.name` and `user.email`, makes an empty commit, `os.chdir`s into it (restored in `finally`) and calls the CLI with `click.testing.CliRunner().invoke(cli, [...])`.
- Drawn kind:
  - stale: `chitty init --autocommit`, then set `chitty_version` in `chitty.toml` to `"0.1.0"` and commit; drawn variations: `AGENTS.md` removed, or with its managed block removed; `.gitignore` removed, or without `.worktrees/`; `CLAUDE.md` removed; an extra `[contexts.extra]` with `prefix = "EXTRA"` whose backlog directory is absent or present (each change committed). The write is `chitty add T -d x`.
  - fresh: no `chitty.toml`. The write is `chitty init --autocommit`.
- Drawn failure:
  - registration: before the write, `register_project(name, other)` (`src/chitty/config.py`) where `other` is another fresh directory and `name` is the `project` read from `chitty.toml` (stale) or `_default_project(root.name)` from `src/chitty/store.py` (fresh).
  - hook (fresh kind only, since the stale kind's failing commit is `TASK-464`'s): `.git/hooks/pre-commit` is an executable script that prints `HOOKSTDERR` to stderr and exits 1, installed before the write.
- Add an `@example` for each kind and failure pair, so every case runs every time.
- Snapshot before and after the write: `git rev-parse HEAD`; `git status --porcelain --untracked-files=all`; for each of `chitty.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`: absent, `os.readlink` when a symlink, else bytes; and the set of directories at or under `chitty/` (an explicit walk, because Git does not show empty directories).

## Acceptance Criteria

- [ ] Property: for every drawn kind and failure, the write exits non-zero with output containing the original message (`is registered to`, or `HOOKSTDERR`), and the snapshot after equals the snapshot before. It fails on `main`: the stale registration case leaves ` M chitty.toml`, and the fresh hook case leaves a `chitty/` directory.
- [ ] With no failure, after the stale `chitty add` autocommits, `git status --porcelain` is empty and `chitty_version` is upgraded; `chitty init --autocommit` on a fresh repository commits `chitty: initialize and enable autocommit`; existing tests in `tests/test_init_workflow.py` and `tests/test_autocommit.py` pass unchanged.
- [ ] Plausible wrong versions, each run against the property, with the failing case and command recorded in a note: today's restore, around the commit only; restoring files but not removing created directories; removing only the leaf backlog directory, not parents created with it (caught by the fresh hook case, where `chitty/` is created with `chitty/tasks`). `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:05Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:06Z sunny-white-dormouse: changed notes
- 2026-11-19T21:06:45Z sunny-white-dormouse: changed title, labels, priority, description, acceptance criteria
- 2026-11-19T21:06:45Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:07:15Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:07:15Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:08:53Z sunny-white-dormouse: changed dependencies, description, acceptance criteria
- 2026-11-19T21:08:53Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:09:02Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:11:40Z sunny-white-dormouse: changed description
- 2026-11-19T21:11:40Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:11:54Z sunny-white-dormouse: changed description
- 2026-11-19T21:11:54Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:17:05Z sunny-white-dormouse: changed title, dependencies, description, acceptance criteria
- 2026-11-19T21:17:05Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:17:27Z sunny-white-dormouse: changed acceptance criteria
- 2026-11-19T21:17:52Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:19:12Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:19:12Z sunny-white-dormouse cold-read → todo
