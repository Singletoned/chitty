---
title: Refuse archiving a `dropped` ticket
status: to-plan
priority: high
depends_on:
  - TASK-599
  - TASK-655
parent: TASK-599
created: 2026-11-24
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close a ticket is `done`, which (with review on) needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. On 2026-11-22 an agent asked to close the superseded `TASK-451` that way was stopped by its own permission check as faking a review; the ticket is still open. Add a terminal status for tickets that will not be done.

Split from `TASK-599` on 2026-11-24; `TASK-599` adds the `dropped` status. This ticket keeps dropped tickets out of the archive.

Decisions:

- Archiving is unchanged (decided with the person, 2026-11-22: dropped tickets must stay visible so we can see whether agents drop tickets that should have been built; when they may be archived or deleted, by age, is `TASK-600`). `chitty archive` with no ID still archives only `done` tickets, so it leaves `dropped` ones in place. `chitty archive <id>` on a `dropped` ticket is refused in every `archive` mode, before anything is written, with `ChittyError` `<id> is dropped; dropped tickets are kept visible and cannot be archived` (in `Repo._set_archived` and before `_delete_done`'s check, so the delete mode gives the same message). That also keeps an archived copy from satisfying a dependency.

Tests in a new `tests/test_status_dropped.py`, inheriting `CliTestCase` from `tests/test_cli.py` (a `RepoTestCase` whose `run_cli` wraps `click.testing.CliRunner`), as `tests/test_edit_human.py` does; the repository is not a Git repository (no `git init`); it is the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`). Every `done` ticket in a fixture is written directly with `status: done` in its frontmatter, since review is on and `chitty add -s done` is refused:

- For the archive cases, write the `dropped` ticket file directly in the fixture (`status: dropped` in its frontmatter).
- `chitty archive` with no ID exits 0, archives a `done` ticket and leaves a `dropped` one in `chitty/tasks/` (this guards today's behaviour, which passes before the change; it must fail against the wrong version where `chitty archive` with no ID archives both `done` and `dropped` tickets, recorded in a note).
- `chitty archive TASK-1` on a dropped ticket exits non-zero, the output contains `TASK-1 is dropped; dropped tickets are kept visible and cannot be archived`, and the file is byte-identical and still in `chitty/tasks/`. Run it once with the default config and once in a repository whose `chitty.toml` sets `archive = "delete"` (the `CONFIG` from `tests/support.py` with that line added).

## Acceptance Criteria

- [ ] `chitty archive TASK-1` on a dropped ticket is refused with its message, the file unchanged and still in `chitty/tasks/`, with `archive = "move"` and with `archive = "delete"`; both fail before the change
- [ ] `chitty archive` with no ID archives the `done` ticket and leaves the `dropped` one, and fails against the wrong version that archives both; record both runs in a note; `make check` passes

## Notes

Planner, 2026-11-24: `TASK-655` now lets a criterion mark tests that pin kept behaviour as regression tests, which must pass but need not fail without the change. When re-planning, mark such tests that way instead of requiring wrong-version runs as review evidence.

Released a planning claim idle since 2026-11-24; TASK-599 and TASK-655 have landed.

## History

- 2026-11-24T08:45:30Z sunny-hazel-gannet → planning
- 2026-11-24T09:27:49Z sunny-hazel-gannet: changed dependencies
- 2026-11-24T22:32:19Z sunny-hazel-gannet: changed notes
- 2026-11-26T19:00:44Z zesty-ginger-newt: changed notes
- 2026-11-26T19:00:44Z zesty-ginger-newt planning → to-plan
