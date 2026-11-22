---
title: Renumber provisional tickets outside Git
status: doing
depends_on:
  - TASK-517
parent: TASK-391
created: 2026-11-22
---

## Description

Split from `TASK-517` on 2026-11-22. `TASK-517` landed `Repo.renumber_provisional()` in `src/chitty/store.py` (rechecked 2026-11-22). This ticket adds characterisation tests for a repository outside Git; a cold reader's probe on `main` showed both behaviours already hold, so no production change is expected.

Tests: a new `RepoTestCase` class in `tests/test_renumber_provisional.py`, setting `CHITTY_ACTOR` (`mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"})`) because `RepoTestCase` clears it. Each test uses a temporary directory with no `.git`, a `chitty.toml` holding `CONFIG` from `tests/support.py`, and one file `chitty/tasks/TASK-AAAAAA--alpha.md` with title `Alpha` and `provisional: true` (the fixture shape in `TestPrepareRenumbering.fixture`).

1. `autocommit = false` (as in `CONFIG`): `renumber_provisional()` returns one `Change` for `TASK-1`; afterwards the directory holds `chitty/tasks/TASK-1--alpha.md` and not the old file, and `.git` does not exist.
2. `autocommit = true` (replace that line of `CONFIG`): raises `ChittyError` whose message contains `requires` and `to be in a Git work tree` (today: "autocommit requires <root> to be in a Git work tree; run `git init` or set `autocommit = false`", from `_prepare_write`); every file's bytes and paths are unchanged and `.git` does not exist.

Out of scope: the `git` binary missing from `PATH`.

These describe landed behaviour, so they pass today. Evidence that they test something: run test 2 with `Repo._prepare_write` patched to do nothing, confirm it fails, and record that run in a note.

## Acceptance Criteria

- [ ] Both tests pass; a note records test 2 failing with `Repo._prepare_write` patched to a no-op; `make check` passes

## History

- 2026-11-22T01:35:29Z lively-zinc-newt → planning
- 2026-11-22T03:20:44Z lively-zinc-newt: changed description
- 2026-11-22T03:20:44Z lively-zinc-newt planning → cold-read
- 2026-11-22T03:21:40Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T03:21:40Z lively-zinc-newt cold-read → todo
- 2026-11-22T03:40:47Z upbeat-navy-urchin todo → doing
