---
title: Find ticket contexts from the files `ticket_ids()` counts, not every ref's history
status: todo
parent: TASK-376
created: 2026-11-20
---

## Description

`Repo.discovered_contexts` (`src/chitty/store.py`) returns the configured contexts, every directory under `chitty/` in the working tree, and every context directory found in any ref's history (`self._history()`, from `git.historical_files`). Every autocommitted write calls it (`Repo._commit` runs `check.fix`, whose `check.check` calls it), as do `context_of`, `chitty list` and `chitty check`. `TASK-376` removes the history scan. `Repo.ticket_ids()` (`TASK-474`) already finds the ticket files that count: the working tree's, `main`'s, and each ticket branch's own file (`_collect_ticket_ids`). This ticket takes context discovery from those paths. It is split out of `TASK-378`, which switches the ticket reads themselves.

Decisions:

- `_collect_ticket_ids` also records the path, relative to `Repo.root`, of every file it counts: working-tree ticket files, `main`'s ticket files, and each ticket branch's own ticket file (the ones it adds to `result`). Store them in a new `self._ticket_paths: set[Path] | None`, set alongside `self._ticket_ids` and cleared with it in `_invalidate`. A new `Repo.ticket_paths() -> set[Path]` calls `ticket_ids()` when needed and returns a copy.
- `discovered_contexts` returns the configured contexts, then each working-tree `chitty/<dir>` directory as today, then `Context(name, "", self.root / BACKLOG_DIR / name)` for each `path.parts[1]` of `ticket_paths()` not already present, in sorted order. It no longer calls `_history()`. It parses no ticket content and chooses no source, so a conflicted ticket or a malformed ticket body cannot make it fail. Filename problems keep raising as today: `_files` already raises on them in every read (checked 2026-11-20: a stray `chitty/tasks/notes.txt` makes `chitty list`, `add` and `edit` fail).
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
- [ ] With `TASK-1` edited on both `task-1` and `main` since they split, a file whose body does not start with `---` committed as `TASK-2` on `main`, and `git.historical_files` patched with `unittest.mock.patch.object` to raise, `Repo.open(root).discovered_contexts()` returns the configured contexts and `other` without raising (fails before the change, by the patched error; the conflicted and malformed tickets are guards that discovery reads no ticket content)
- [ ] The migrated test in `tests/test_unconfigured_directories.py` passes and asserts the new behaviour, and `make check` passes

## History

- 2026-11-20T22:56:54Z quick-pearl-lapwing → planning
- 2026-11-20T22:57:07Z quick-pearl-lapwing: changed description
- 2026-11-20T22:57:07Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T22:58:02Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T22:58:02Z quick-pearl-lapwing cold-read → todo
