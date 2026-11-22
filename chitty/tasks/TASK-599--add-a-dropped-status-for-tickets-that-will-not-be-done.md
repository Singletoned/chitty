---
title: Add a `dropped` status for tickets that will not be done
status: todo
labels:
  - needs-minor
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close a ticket is `done`, which (with review on) needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. On 2026-11-22 an agent asked to close the superseded `TASK-451` that way was stopped by its own permission check as faking a review; the ticket is still open. Add a terminal status for tickets that will not be done.

Decisions:

- New status `dropped`, last in `STATUSES` in `src/chitty/model.py`, and in the frontmatter `status` `Literal` (`src/chitty/model.py`, around line 172). The MCP `Status` `Literal` (`src/chitty/mcp.py`) is a separate ticket. Glyph `🚫` (U+1F6AB, an emoji-presentation character, so it needs no variation selector) in `STATUS_GLYPHS`; label `drop` in `STATUS_LABELS`. Not in `DEFAULT_LIST_STATUSES`, so `chitty list` hides it as it hides `done`; `chitty list -s dropped` and `--all` show it.
- `chitty edit <id> -s dropped` is allowed from every status except `done` (`dropped` from `done` raises `ChittyError` `<id> is done; it cannot be dropped`), and never needs `review`. It needs a reason: after the edit is applied, the ticket must have a non-empty Summary section, either set by this edit (`--summary`/`--summary-file`) or already there; a Summary that is empty after stripping whitespace counts as empty (`--summary ""` removes it, so that is refused). `chitty add` has no `--summary` option, so `chitty add -s dropped` is refused with `ChittyError` `create the ticket, then drop it with chitty edit -s dropped --summary`; nothing is written. Otherwise it raises `ChittyError` `dropping <id> needs a --summary saying why`, and nothing is written. `-s dropped` on a ticket already `dropped` behaves as setting any status to its current value does today. Leaving `dropped` for another status is allowed as for any status (a ticket can be revived).
- Nothing else changes in this ticket: the runner selects only `todo` and `doing` to work and `review` to review (`src/chitty/selection.py`), so it never picks a dropped ticket. A ticket that depends on a dropped ticket stays blocked, since only `done` or archived satisfies a dependency (`src/chitty/store.py`, `_dependency_is_done` and the function after it, which test `archived` or `status == "done"`); an implementation that counted `dropped` as satisfied would be wrong; how dependents and release labels treat `dropped` is a later ticket.
- Archiving is unchanged (decided with the person, 2026-11-22: dropped tickets must stay visible so we can see whether agents drop tickets that should have been built; when they may be archived or deleted, by age, is `TASK-600`). `chitty archive` with no ID still archives only `done` tickets, so it leaves `dropped` ones in place.
- The ticket's branch and worktree, if any, are not touched; the clean-up rule in `AGENTS.md` covers them. Editing a ticket whose latest copy is on a branch is still refused from the main checkout, as for any edit (`TASK-385` covers that).

Tests in a new `tests/test_status_dropped.py`, using `RepoTestCase` and `chitty.cli.cli` through `click.testing.CliRunner` as `tests/test_edit_human.py` does, in the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`):

- From each of `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error` and `review`: `chitty edit TASK-1 -s dropped --summary "Superseded by TASK-2."` exits 0; the file has `status: dropped`, its Summary section is `Superseded by TASK-2.`, and its History has the transition.
- Without `--summary` on a ticket with no Summary: exits non-zero, the output contains `dropping TASK-1 needs a --summary saying why`, and the file is byte-identical to before (the message is what tells this apart from today's invalid-choice error). On a ticket that already has a Summary: exits 0. On a ticket that already has a Summary, `--summary ""`, and on a ticket with no Summary, `--summary "   "`: each refused with the same message, file byte-identical. `chitty add -s dropped` is refused, its output contains `create the ticket, then drop it with chitty edit -s dropped --summary`, and it creates no file. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 -s dropped` exits 0 and the status stays `dropped`.
- From `done`: refused, the output contains `TASK-1 is done; it cannot be dropped`, file byte-identical.
- For the list and archive cases, write the `dropped` ticket file directly in the fixture (`status: dropped` in its frontmatter), since before the change the CLI cannot make one. `chitty list` does not show a dropped ticket; `chitty list -s dropped` and `chitty list --all` do, with `🚫` and `drop`.
- `chitty archive` with no ID archives a `done` ticket and leaves a `dropped` one in `chitty/tasks/` (it fails before the change only because the fixture cannot be parsed yet).
- `chitty edit TASK-1 -s todo` from `dropped` exits 0.
- A `todo` ticket `TASK-2` with `depends_on: [TASK-1]`, where `TASK-1` is `dropped`: `chitty next --mode work` does not print `TASK-2` (guards the unchanged dependency rule).
- The model round-trips: `chitty.model.parse(text).render()` keeps `status: dropped`. It fails before the change: `parse` validates the status through `Frontmatter.model_validate`, which rejects `dropped`.

Docs: the `- Statuses:` bullet in `docs/plan/task-file.md` (below the `## Frontmatter` table) and the `chitty --help` text for `-s`, if it lists statuses, name `dropped` and say what it is for. The role guides are a later ticket.

## Acceptance Criteria

- [ ] Edit and add rules: the `tests/test_status_dropped.py` cases for every allowed starting status, the summary refusals (none, `""`, whitespace), the refusal from `done`, `-s dropped` on a dropped ticket and the `add -s dropped` refusal pass, each asserting its message, and fail before the change
- [ ] The `- Statuses:` bullet in `docs/plan/task-file.md` lists `dropped` and says in one clause it is for tickets that will not be done, with a Summary saying why; `make check` passes
- [ ] List, archive, revive and dependency: the `tests/test_status_dropped.py` cases for `chitty list`, `-s dropped` and `--all`, `chitty archive` leaving the dropped ticket, `-s todo` from `dropped`, the dependent `TASK-2` and the round-trip pass, and fail before the change (some only because `dropped` cannot be parsed yet). Record both runs in a note

## Notes

Planning blocker: the archive requirements cover both archive commands without restricting the archive configuration, but the specified tests use only the default move mode. In `src/chitty/store.py`, `_archive` calls `_delete_done` for `archive = "delete"`, and `_delete_done` rejects every status other than `done` and removes dependency references on deletion. Please specify the intended dropped-ticket behavior in delete mode and the fixture, action and assertions for both explicit-ID and bulk archive, including dependent tickets. This matters because the ticket also says a dependency on a dropped ticket stays blocked and nothing else changes. The explicit-ID archive and `list --all` requirements also lack described test cases; please specify their fixture, action and assertions. The same-status dropped edit requirement has no described test for its behavior, including whether a missing or removed summary is allowed; please specify that test and resolve the interaction with the summary rule.

Independent inspection: model validation currently rejects dropped, list choices come from `STATUSES`, bulk archive filters done, and dependency satisfaction checks done or archived. The CLI add command currently has no summary option, so it must gain one to satisfy the stated add case. No implementation or regression run was attempted: the archive and same-status expectations are not sufficiently specified to verify all requirements. Runner and review execution beyond source inspection was not checked.

Planner, 2026-11-22: blocker resolved by taking archiving of dropped tickets out of scope (the person wants dropped tickets kept visible; `TASK-600` decides archiving by age), by refusing `chitty add -s dropped`, and by specifying the same-status and `list --all` cases.

## History

- 2026-11-22T22:09:08Z plucky-umber-wren → cold-read
- 2026-11-22T22:10:24Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:11:29Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:12:51Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:12:51Z plucky-umber-wren cold-read → todo
- 2026-11-22T22:13:06Z plucky-umber-wren: changed acceptance criteria
- 2026-11-22T22:13:34Z zesty-ochre-heron todo → doing
- 2026-11-22T22:16:03Z zesty-ochre-heron: changed owner, notes
- 2026-11-22T22:16:03Z zesty-ochre-heron doing → planning
- 2026-11-22T22:48:57Z plucky-umber-wren: changed description, acceptance criteria, notes
- 2026-11-22T22:48:57Z plucky-umber-wren planning → cold-read
- 2026-11-22T22:50:07Z plucky-umber-wren: changed description, acceptance criteria
- 2026-11-22T22:50:07Z plucky-umber-wren cold-read → todo
- 2026-11-22T22:50:17Z plucky-umber-wren: changed description
