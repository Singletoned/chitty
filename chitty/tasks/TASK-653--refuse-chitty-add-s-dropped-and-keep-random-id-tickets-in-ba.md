---
title: Refuse `chitty add -s dropped`, and keep random-ID tickets in `backlog`
status: planning
priority: high
depends_on:
  - TASK-599
  - TASK-655
parent: TASK-599
created: 2026-11-24
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close a ticket is `done`, which (with review on) needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. On 2026-11-22 an agent asked to close the superseded `TASK-451` that way was stopped by its own permission check as faking a review; the ticket is still open. Add a terminal status for tickets that will not be done.

Split from `TASK-599` on 2026-11-24; `TASK-599` adds the `dropped` status. This ticket refuses creating a ticket as `dropped` and keeps the random-ID rule.

Decisions:

- `chitty add` has no `--summary` option, so `chitty add -s dropped` is refused with `ChittyError` `create the ticket, then drop it with chitty edit -s dropped --summary`; nothing is written. The check lives in `Repo.add` in `src/chitty/store.py`, before the line that forces a random-ID ticket to `backlog`. The CLI checks `--description` first (`add` in `src/chitty/cli.py`), so in a sequential context `chitty add T -s dropped` without `-d` keeps today's usage error; that is unchanged, and the tests pass `-d x`.
- Random-ID contexts (`random_ids = true`, such as `backlog`) keep their rule that a ticket there has status `backlog` (decided with the person, 2026-11-23: contexts are being removed by `TASK-262` and `TASK-267`, so no exception is added). `chitty edit <id> -s dropped` on such a ticket is refused by the existing check in `Repo._edit_stored`, with its existing `chitty move <id> tasks` message; the rules above apply to sequential contexts. `chitty add -s dropped` is refused in every context, checked before `Repo.add` forces a random-ID ticket to `backlog`, so `chitty add -c backlog -s dropped` gives the same refusal message instead of a silent `backlog` ticket.

Tests in a new `tests/test_status_dropped.py`, inheriting `CliTestCase` from `tests/test_cli.py` (a `RepoTestCase` whose `run_cli` wraps `click.testing.CliRunner`), as `tests/test_edit_human.py` does; the repository is not a Git repository (no `git init`); it is the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`). Every `done` ticket in a fixture is written directly with `status: done` in its frontmatter, since review is on and `chitty add -s done` is refused:

- `chitty add T -d x -s dropped` is refused, its output contains `create the ticket, then drop it with chitty edit -s dropped --summary`, and it creates no file.
- Random-ID context, in a repository whose `chitty.toml` adds the `BACKLOG` table from `tests/test_backlog_context.py` (`prefix = "BACKLOG"`, `random_ids = true`), with `chitty.store._random_number` patched as that file does: `chitty add Idea -c backlog -s dropped` exits non-zero, its output contains `create the ticket, then drop it with chitty edit -s dropped --summary`, and no file is created in `chitty/backlog/` (fails before the change, which creates a `backlog` ticket; so would a check placed after that coercion). For a `backlog` ticket there, `chitty edit <id> -s dropped --summary "x"` exits non-zero, its output contains `chitty move <id> tasks`, and the file is byte-identical (passes before the change, because the existing check refuses it; it must fail against the wrong version that exempts `dropped` from the random-ID rule, recorded in a note).

## Acceptance Criteria

- [ ] The `chitty add T -d x -s dropped` and `chitty add Idea -c backlog -s dropped` cases pass, each asserting its message and that no file is written, and fail before the change
- [ ] The `-s dropped` case on a `backlog`-context ticket passes, and fails against the wrong version that exempts `dropped` from the random-ID rule; record both runs in a note; `make check` passes

## Notes

Planner, 2026-11-24: `TASK-655` now lets a criterion mark tests that pin kept behaviour as regression tests, which must pass but need not fail without the change. When re-planning, mark such tests that way instead of requiring wrong-version runs as review evidence.

## History

- 2026-11-24T08:45:27Z sunny-hazel-gannet → planning
- 2026-11-24T09:27:45Z sunny-hazel-gannet: changed dependencies
- 2026-11-24T22:32:17Z sunny-hazel-gannet: changed notes
