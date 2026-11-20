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

- Wrap everything in `init_repo` from the first write to disk to the end of the function, including `register_project` and, when `enable_autocommit` is true, its own commit, in one `try` (the stale case reaches `init_repo` through `_prepare_write` with autocommit off and fails at `register_project`), with `except BaseException:` that restores and re-raises the original exception (replacing today's `except ChittyError` around the commit).
- Restore means: each path in `originals` (`chitty.toml`, `pyproject.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`) goes back to its `_file_state` with `_restore_file`; and every directory this call created is removed. `init_repo` creates backlog context directories with `mkdir(parents=True)`, so record each directory, parents included, that did not exist just before its `mkdir`, and remove them deepest first, only when empty.
- `init_repo` computes `originals` twice; keep only the second (both precede any write).
- Out of scope: the inbox registration under `XDG_DATA_HOME` (outside the repository, so outside the snapshot on purpose) is not undone; a `chitty/` path that is a file rather than a directory; `pyproject.toml` (`[tool.chitty]`) setups are not drawn by the test.

Tests. Hypothesis (the repository tool), in a new `tests/test_property_init_restore.py`, in a class inheriting `RepoTestCase` (`tests/support.py`), with real Git and real failures, no mocking of files.

- Each example builds its own state: a fresh directory from `tempfile.mkdtemp(dir=self.tmp)` as the repository, and a fresh data directory set as `XDG_DATA_HOME` with `mock.patch.dict(os.environ, ...)` for that example only, so registrations never carry over between examples. It runs `git init`, sets `user.name` and `user.email`, makes an empty commit, `os.chdir`s into it (restored in `finally`) and calls the CLI with `click.testing.CliRunner().invoke(cli, [...])`.
- Drawn kind:
  - stale: `chitty init --autocommit`, then set `chitty_version` in `chitty.toml` to `"0.1.0"` and commit; drawn variations: `AGENTS.md` removed, or with its managed block removed; `.gitignore` removed, or without `.worktrees/`; `CLAUDE.md` removed; an extra `[contexts.extra]` with `prefix = "EXTRA"` whose backlog directory is absent or present (each change committed). The write is `chitty add T -d x`.
  - fresh: no `chitty.toml`. The write is `chitty init --autocommit`.
- Drawn failure:
  - registration: before the write, make the project name belong to `other`, another fresh directory. Fresh kind: call `register_project(name, other)` (`src/chitty/config.py`) with `name = _default_project(root.name)` from `src/chitty/store.py`. Stale kind: `chitty init --autocommit` has already registered `name` (the `project` read from `chitty.toml`) to the test repository, so `register_project(name, other)` would raise in the fixture; instead overwrite the owner file `config.inbox_path(name) / "repo"` with `str(other.resolve()) + "\n"`, which is the state a second clone of the same project meets (decided 2026-11-20 after a worker found the fixture raised before the write).
  - hook (fresh kind only, since the stale kind's failing commit is `TASK-464`'s): `.git/hooks/pre-commit` is an executable script that prints `HOOKSTDERR` to stderr and exits 1, installed before the write.
- Add an `@example` for each kind and failure pair, so every case runs every time.
- Snapshot before and after the write: `git rev-parse HEAD`; `git status --porcelain --untracked-files=all`; for each of `chitty.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`: absent, `os.readlink` when a symlink, else bytes; and the set of directories at or under `chitty/` (an explicit walk, because Git does not show empty directories).

## Acceptance Criteria

- [ ] Property: for every drawn kind and failure, the write exits non-zero with output containing the original message (`is registered to`, or `HOOKSTDERR`), and the snapshot after equals the snapshot before. It fails on `main`: the stale registration case leaves ` M chitty.toml`, and the fresh hook case leaves a `chitty/` directory.
- [ ] With no failure, after the stale `chitty add` autocommits, `git status --porcelain` is empty and `chitty_version` is upgraded; `chitty init --autocommit` on a fresh repository commits `chitty: initialize and enable autocommit`; existing tests in `tests/test_init_workflow.py` and `tests/test_autocommit.py` pass unchanged.
- [ ] Plausible wrong versions, each run against the property, with the failing case and command recorded in a note: today's restore, around the commit only; restoring only `chitty.toml` and created directories, not `AGENTS.md`, `.gitignore` or `CLAUDE.md` (caught only by the fresh hook case, since the stale registration failure happens before those three are written); restoring files but not removing created directories; removing only the leaf backlog directory, not parents created with it (caught by the fresh hook case, where `chitty/` is created with `chitty/tasks`). `make check` passes.

## Plan

Add the specified isolated real-Git property tests and confirm failures before implementing a rollback around setup writes, tracking all newly created directories. Exercise the specified wrong implementations, successful paths, and full checks before handoff.

## Notes

Suggestion origin: chitty

Implementation has not started. The initial edit attempt changed indentation incorrectly and was discarded; ticket requirements and existing init_repo/test patterns were inspected. No code or tests have been changed.

Back to planning review 2026-11-20: the previous worker returned it without starting, and named no ticket defect. Branch rebased onto `main`; claims rechecked against the code.

Planning needed: the specified stale registration fixture cannot be constructed as written. Its initial `chitty init --autocommit` registers the project to the test repository in the example's fresh `XDG_DATA_HOME`; the subsequent required `register_project(name, other)` raises `ChittyError` immediately because that name already belongs to the first repository. Thus the test never reaches the write being tested. Decide how the fixture should replace or isolate that initial registration before registering `other`, including the intended action and assertions. A trial property confirmed this setup error; its fresh hook example did reach the write and failed on the original code because the `chitty/` directories remained. The incomplete trial test was discarded; no implementation changes were made and wrong-version, success-path and full-check verification remain unfinished.

The stale registration fixture is impossible as specified: initial `chitty init --autocommit` registers the project to the test repository, so `register_project(name, other)` raises before the tested write. The planner must decide how to replace or isolate the initial registration and specify the fixture action and assertions. A trial confirmed this error and also confirmed the fresh hook example fails on the original code due to leftover directories. The incomplete trial test was discarded; no implementation changes were made. Wrong-version, success-path and full-check verification remain unfinished.

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
- 2026-11-19T23:16:08Z brisk-khaki-urchin todo → doing
- 2026-11-19T23:17:41Z brisk-khaki-urchin: wrote the plan
- 2026-11-19T23:18:27Z brisk-khaki-urchin: changed owner, notes
- 2026-11-19T23:18:27Z brisk-khaki-urchin doing → planning
- 2026-11-20T22:34:18Z quick-pearl-lapwing: changed notes
- 2026-11-20T22:34:18Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:35:13Z quick-pearl-lapwing: changed description
- 2026-11-20T22:35:13Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T22:38:52Z brisk-coral-eel todo → doing
- 2026-11-20T22:40:57Z brisk-coral-eel: wrote the plan
- 2026-11-20T22:41:46Z brisk-coral-eel: changed notes
- 2026-11-20T22:41:56Z brisk-coral-eel: changed owner, notes
- 2026-11-20T22:41:56Z brisk-coral-eel doing → planning
- 2026-11-20T23:14:11Z quick-pearl-lapwing: changed description
- 2026-11-20T23:14:11Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:16:22Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-20T23:16:22Z quick-pearl-lapwing cold-read → todo
