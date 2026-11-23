---
title: Add a `dropped` status for tickets that will not be done
status: doing
labels:
  - needs-minor
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close a ticket is `done`, which (with review on) needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. On 2026-11-22 an agent asked to close the superseded `TASK-451` that way was stopped by its own permission check as faking a review; the ticket is still open. Add a terminal status for tickets that will not be done.

Decisions:

- New status `dropped`, last in `STATUSES` in `src/chitty/model.py`, and in the frontmatter `status` `Literal` (`src/chitty/model.py`, around line 172). The MCP `Status` `Literal` (`src/chitty/mcp.py`) is a separate ticket. Glyph `🚫` (U+1F6AB, an emoji-presentation character, so it needs no variation selector) in `STATUS_GLYPHS`; label `drop` in `STATUS_LABELS`. Not in `DEFAULT_LIST_STATUSES`, so `chitty list` hides it as it hides `done`; `chitty list -s dropped` and `--all` show it.
- `chitty edit <id> -s dropped` is allowed from every status except `done` (`dropped` from `done` raises `ChittyError` `<id> is done; it cannot be dropped`), and never needs `review`. It needs a reason: after the edit is applied, the ticket must have a non-empty Summary section, either set by this edit (`--summary`/`--summary-file`) or already there; a Summary that is empty after stripping whitespace counts as empty (`--summary ""` removes it, so that is refused). `chitty add` has no `--summary` option, so `chitty add -s dropped` is refused with `ChittyError` `create the ticket, then drop it with chitty edit -s dropped --summary`; nothing is written. Otherwise it raises `ChittyError` `dropping <id> needs a --summary saying why`, and nothing is written. The Summary rule applies to every edit whose resulting status is `dropped`, including edits to a ticket that is already `dropped` with or without `-s`: `--summary ""` on a dropped ticket is refused, and so is any edit (for example `--note x`) to a dropped ticket that has no Summary. With a Summary, `-s dropped` on an already dropped ticket is accepted and leaves the status `dropped`, as setting a status to its current value does today. Leaving `dropped` for another status is allowed as for any status (a ticket can be revived); `-s done` from `dropped` follows the review rule it follows today.
- Nothing else changes in this ticket: the runner selects only `todo` and `doing` to work and `review` to review (`src/chitty/selection.py`), so it never picks a dropped ticket. A ticket that depends on a dropped ticket stays blocked, since only `done` or archived satisfies a dependency (`src/chitty/store.py`, `_dependency_is_done` and the function after it, which test `archived` or `status == "done"`); an implementation that counted `dropped` as satisfied would be wrong; how dependents and release labels treat `dropped` is a later ticket.
- Archiving is unchanged (decided with the person, 2026-11-22: dropped tickets must stay visible so we can see whether agents drop tickets that should have been built; when they may be archived or deleted, by age, is `TASK-600`). `chitty archive` with no ID still archives only `done` tickets, so it leaves `dropped` ones in place. `chitty archive <id>` on a `dropped` ticket is refused in every `archive` mode, before anything is written, with `ChittyError` `<id> is dropped; dropped tickets are kept visible and cannot be archived` (in `Repo._set_archived` and before `_delete_done`'s check, so the delete mode gives the same message). That also keeps an archived copy from satisfying a dependency.
- The ticket's branch and worktree, if any, are not touched; the clean-up rule in `AGENTS.md` covers them. Editing a ticket whose latest copy is on a branch is still refused from the main checkout, as for any edit (`TASK-385` covers that).

Tests in a new `tests/test_status_dropped.py`, using `RepoTestCase` and `chitty.cli.cli` through `click.testing.CliRunner` as `tests/test_edit_human.py` does, in the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`):

- From each of `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error` and `review`: `chitty edit TASK-1 -s dropped --summary "Superseded by TASK-2."` exits 0; the file has `status: dropped`, its Summary section is `Superseded by TASK-2.`, and its History has the transition.
- Without `--summary` on a ticket with no Summary: exits non-zero, the output contains `dropping TASK-1 needs a --summary saying why`, and the file is byte-identical to before (the message is what tells this apart from today's invalid-choice error). On a ticket that already has a Summary: exits 0. On a ticket that already has a Summary, `--summary ""`, and on a ticket with no Summary, `--summary "   "`: each refused with the same message, file byte-identical. `chitty add -s dropped` is refused, its output contains `create the ticket, then drop it with chitty edit -s dropped --summary`, and it creates no file. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 -s dropped` exits 0 and the status stays `dropped`. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 --summary ""` is refused with the same message, file byte-identical. On a `dropped` ticket file written with no Summary, and on one written with a `## Summary` heading followed only by blank and space-only lines, `chitty edit TASK-1 --note x` is refused with the same message, file byte-identical.
- From `done`: refused, the output contains `TASK-1 is done; it cannot be dropped`, file byte-identical.
- For the list and archive cases, write the `dropped` ticket file directly in the fixture (`status: dropped` in its frontmatter), since before the change the CLI cannot make one. `chitty list` does not show a dropped ticket; `chitty list -s dropped` and `chitty list --all` do, with `🚫` and `drop`.
- `chitty archive` with no ID archives a `done` ticket and leaves a `dropped` one in `chitty/tasks/` (it fails before the change only because the fixture cannot be parsed yet).
- `chitty archive TASK-1` on a dropped ticket exits non-zero, the output contains `TASK-1 is dropped; dropped tickets are kept visible and cannot be archived`, and the file is byte-identical and still in `chitty/tasks/`. Run it once with the default config and once in a repository whose `chitty.toml` sets `archive = "delete"` (the `CONFIG` from `tests/support.py` with that line added).
- `chitty edit TASK-1 -s todo` from `dropped` exits 0.
- A `todo` ticket `TASK-2` with `depends_on: [TASK-1]`, where `TASK-1` is `dropped`: `chitty next --mode work` does not print `TASK-2` (guards the unchanged dependency rule).
- The model round-trips: `chitty.model.parse(text).render()` keeps `status: dropped`. It fails before the change: `parse` validates the status through `Frontmatter.model_validate`, which rejects `dropped`.

Docs: the `- Statuses:` bullet in `docs/plan/task-file.md` (below the `## Frontmatter` table) and the `chitty --help` text for `-s`, if it lists statuses, name `dropped` and say what it is for. The role guides are a later ticket.

## Acceptance Criteria

- [ ] Edit rules: the `tests/test_status_dropped.py` cases for every allowed starting status and the refusal from `done` pass, each asserting its message, and fail before the change
- [ ] The `- Statuses:` bullet in `docs/plan/task-file.md` lists `dropped` and says in one clause it is for tickets that will not be done, with a Summary saying why; `make check` passes
- [ ] List, archive, revive and dependency: the `tests/test_status_dropped.py` cases for `chitty list`, `-s dropped` and `--all`, `chitty archive` leaving the dropped ticket, `-s todo` from `dropped`, the dependent `TASK-2` and the round-trip pass, and fail before the change (some only because `dropped` cannot be parsed yet). Record both runs in a note
- [ ] Summary rules: the `tests/test_status_dropped.py` cases for the summary refusals (none, `""`, whitespace, a whitespace-only Summary in the file), `-s dropped` and `--summary ""` on a dropped ticket, `--note` on a dropped ticket with no Summary, and the `add -s dropped` refusal pass, each asserting its message, and fail before the change. Record both runs in a note

## Plan

Add regression coverage for dropped status before implementing model, edit and archive validation; update the status documentation, run formatting and checks, then hand off for review.

## Notes

Planning blocker: the archive requirements cover both archive commands without restricting the archive configuration, but the specified tests use only the default move mode. In `src/chitty/store.py`, `_archive` calls `_delete_done` for `archive = "delete"`, and `_delete_done` rejects every status other than `done` and removes dependency references on deletion. Please specify the intended dropped-ticket behavior in delete mode and the fixture, action and assertions for both explicit-ID and bulk archive, including dependent tickets. This matters because the ticket also says a dependency on a dropped ticket stays blocked and nothing else changes. The explicit-ID archive and `list --all` requirements also lack described test cases; please specify their fixture, action and assertions. The same-status dropped edit requirement has no described test for its behavior, including whether a missing or removed summary is allowed; please specify that test and resolve the interaction with the summary rule.

Independent inspection: model validation currently rejects dropped, list choices come from `STATUSES`, bulk archive filters done, and dependency satisfaction checks done or archived. The CLI add command currently has no summary option, so it must gain one to satisfy the stated add case. No implementation or regression run was attempted: the archive and same-status expectations are not sufficiently specified to verify all requirements. Runner and review execution beyond source inspection was not checked.

Planner, 2026-11-22: blocker resolved by taking archiving of dropped tickets out of scope (the person wants dropped tickets kept visible; `TASK-600` decides archiving by age), by refusing `chitty add -s dropped`, and by specifying the same-status and `list --all` cases.

Planning blocker: the revised ticket says archiving is unchanged and dropped tickets must stay visible, but explicit `chitty archive TASK-1` in the default move mode calls `Repo._set_archived`, which accepts any status and moves the file into the archive. `_dependency_is_done` then treats it as satisfied. Delete mode instead refuses non-done tickets. Please decide whether explicit archiving of dropped tickets remains allowed (and qualify the visibility and dependency claims) or is refused, and specify the fixture, action and assertions for the intended behavior. Bulk archive alone does not test this conflict.

The requirement that after an edit to dropped the Summary must be non-empty also conflicts with saying a same-status edit behaves as today: `Edit.apply` permits removing Summary with `--summary ""`. The specified same-status test covers only an existing nonempty Summary without an edit. Please specify whether removing or omitting an absent Summary on an already-dropped ticket is refused, and the corresponding fixture, action and assertions.

Independent inspection: `STATUSES` drives CLI choices and list rendering; model frontmatter validates status separately; selection only uses review, doing and todo; dependency checks accept only done or archived; bulk archive filters done. The add and edit summary cases and model round-trip have described fixtures and assertions. No code or tests were changed or run; the conflicting explicit archive and same-status cases cannot be verified until resolved.

Planner, 2026-11-23: both blockers are resolved. (1) `chitty archive <id>` refuses a dropped ticket in every archive mode, with a stated message and a test for each mode, so dropped tickets stay visible and never satisfy a dependency. (2) The Summary rule applies to every edit whose result is `dropped`, including edits to a ticket already dropped. The contradictory "behaves as today" sentence is gone, and two tests are added.

Planner, 2026-11-23: a cold read found nothing blocking. Added a case for a whitespace-only Summary in the file, said that `-s done` from `dropped` follows the review rule, and split the edit and Summary cases into separate criteria.

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
- 2026-11-22T22:51:01Z lively-indigo-raven todo → doing
- 2026-11-22T22:53:14Z lively-indigo-raven: changed owner, notes
- 2026-11-22T22:53:14Z lively-indigo-raven doing → planning
- 2026-11-23T12:03:58Z witty-russet-gannet: changed description, notes
- 2026-11-23T12:06:14Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:06:14Z witty-russet-gannet planning → todo
- 2026-11-23T12:19:34Z jolly-teal-quail todo → doing
- 2026-11-23T12:22:57Z jolly-teal-quail: wrote the plan
