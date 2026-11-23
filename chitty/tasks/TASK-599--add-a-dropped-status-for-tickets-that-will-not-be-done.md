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
- `chitty edit <id> -s dropped` is allowed from every status except `done` (`dropped` from `done` raises `ChittyError` `<id> is done; it cannot be dropped`), and never needs `review`. It needs a reason: after the edit is applied, the ticket must have a non-empty Summary section, either set by this edit (`--summary`/`--summary-file`) or already there; a Summary that is empty after stripping whitespace counts as empty (`--summary ""` removes it, so that is refused). `chitty add` has no `--summary` option, so `chitty add -s dropped` is refused with `ChittyError` `create the ticket, then drop it with chitty edit -s dropped --summary`; nothing is written. The CLI checks `--description` first (`add` in `src/chitty/cli.py`), so in a sequential context `chitty add T -s dropped` without `-d` keeps today's usage error; that is unchanged, and the tests pass `-d x`. Otherwise it raises `ChittyError` `dropping <id> needs a --summary saying why`, and nothing is written. The Summary rule applies to every edit whose resulting status is `dropped`, including edits to a ticket that is already `dropped` with or without `-s`: `--summary ""` on a dropped ticket is refused, and so is any edit (for example `--note x`) to a dropped ticket that has no Summary. With a Summary, `-s dropped` on an already dropped ticket is accepted and leaves the status `dropped`, as setting a status to its current value does today. Leaving `dropped` for another status is allowed as for any status (a ticket can be revived); `-s done` from `dropped` follows the review rule it follows today.
- Random-ID contexts (`random_ids = true`, such as `backlog`) keep their rule that a ticket there has status `backlog` (decided with the person, 2026-11-23: contexts are being removed by `TASK-262` and `TASK-267`, so no exception is added). `chitty edit <id> -s dropped` on such a ticket is refused by the existing check in `Repo._edit_stored`, with its existing `chitty move <id> tasks` message; the rules above apply to sequential contexts. `chitty add -s dropped` is refused in every context, checked before `Repo.add` forces a random-ID ticket to `backlog`, so `chitty add -c backlog -s dropped` gives the same refusal message instead of a silent `backlog` ticket.
- Where the checks live, all in `src/chitty/store.py` (`AGENTS.md`: behaviour lives in the store): the `add` refusal in `Repo.add`, before the line that forces a random-ID ticket to `backlog`; the `done` refusal, then the Summary rule, in `Repo._edit_stored`, on the task after the edit is applied, stripping the Summary read from the file with `str.strip()` (`model.parse` keeps a whitespace-only Summary as written).
- `chitty summary`: appending `dropped` to `STATUSES` makes `summarize` (which ranks `reversed(TASK_STATUSES)`) list a `dropped` section before `done`; keep that, as both are final.
- Locks: `_edit_stored` checks no run lock for any status change today; dropping a `doing` or `review` ticket that a run holds follows the same rule (allowed). Not changed here.
- Nothing else changes in this ticket: the runner selects only `todo` and `doing` to work and `review` to review (`src/chitty/selection.py`), so it never picks a dropped ticket. A ticket that depends on a dropped ticket stays blocked, since only `done` or archived satisfies a dependency (`src/chitty/store.py`, `_dependency_is_done` and the function after it, which test `archived` or `status == "done"`); an implementation that counted `dropped` as satisfied would be wrong; how dependents and release labels treat `dropped` is a later ticket.
- Archiving is unchanged (decided with the person, 2026-11-22: dropped tickets must stay visible so we can see whether agents drop tickets that should have been built; when they may be archived or deleted, by age, is `TASK-600`). `chitty archive` with no ID still archives only `done` tickets, so it leaves `dropped` ones in place. `chitty archive <id>` on a `dropped` ticket is refused in every `archive` mode, before anything is written, with `ChittyError` `<id> is dropped; dropped tickets are kept visible and cannot be archived` (in `Repo._set_archived` and before `_delete_done`'s check, so the delete mode gives the same message). That also keeps an archived copy from satisfying a dependency.
- The ticket's branch and worktree, if any, are not touched; the clean-up rule in `AGENTS.md` covers them. Editing a ticket whose latest copy is on a branch is still refused from the main checkout, as for any edit (`TASK-385` covers that).

Tests in a new `tests/test_status_dropped.py`, inheriting `CliTestCase` from `tests/test_cli.py` (a `RepoTestCase` whose `run_cli` wraps `click.testing.CliRunner`), as `tests/test_edit_human.py` does; the repository is not a Git repository (no `git init`), so dependencies read the working files, in the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`). Every `done` ticket in a fixture is written directly with `status: done` in its frontmatter, since review is on and `chitty add -s done` is refused:

- From each of `backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error` and `review`: `chitty edit TASK-1 -s dropped --summary "Superseded by TASK-2."` exits 0; the file has `status: dropped`, its Summary section is `Superseded by TASK-2.`, and its History has the transition.
- Without `--summary` on a ticket with no Summary: exits non-zero, the output contains `dropping TASK-1 needs a --summary saying why`, and the file is byte-identical to before (the message is what tells this apart from today's invalid-choice error). On a ticket that already has a Summary: exits 0. On a ticket that already has a Summary, `--summary ""`, and on a ticket with no Summary, `--summary "   "`: each refused with the same message, file byte-identical. `chitty add T -d x -s dropped` is refused, its output contains `create the ticket, then drop it with chitty edit -s dropped --summary`, and it creates no file. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 -s dropped` exits 0 and the status stays `dropped`. On a ticket already `dropped` with a Summary, `chitty edit TASK-1 --summary ""` is refused with the same message, file byte-identical. On a `dropped` ticket file written with no Summary, and on one written with a `## Summary` heading followed only by blank and space-only lines, `chitty edit TASK-1 --note x` is refused with the same message, file byte-identical.
- From `done`, with `--summary "x"` (so only the `done` rule can refuse): refused, the output contains `TASK-1 is done; it cannot be dropped`, file byte-identical.
- For the list and archive cases, write the `dropped` ticket file directly in the fixture (`status: dropped` in its frontmatter), since before the change the CLI cannot make one. `chitty list` does not show a dropped ticket; `chitty list -s dropped` and `chitty list --all` do, with `🚫` and `drop`.
- `chitty archive` with no ID exits 0, archives a `done` ticket and leaves a `dropped` one in `chitty/tasks/` (it fails before the change only because the fixture cannot be parsed yet).
- `chitty archive TASK-1` on a dropped ticket exits non-zero, the output contains `TASK-1 is dropped; dropped tickets are kept visible and cannot be archived`, and the file is byte-identical and still in `chitty/tasks/`. Run it once with the default config and once in a repository whose `chitty.toml` sets `archive = "delete"` (the `CONFIG` from `tests/support.py` with that line added).
- `chitty edit TASK-1 -s todo` from `dropped` exits 0.
- A `todo` ticket `TASK-2` with `depends_on: [TASK-1]`, where `TASK-1` is `dropped`, plus an independent `todo` ticket `TASK-3`: `chitty next --mode work` exits 0 and prints `work TASK-3` (guards the unchanged dependency rule). Positive control: the same fixture without `TASK-3` and with `TASK-1` `done` prints `work TASK-2`.
- Random-ID context, in a repository whose `chitty.toml` adds the `BACKLOG` table from `tests/test_backlog_context.py` (`prefix = "BACKLOG"`, `random_ids = true`), with `chitty.store._random_number` patched as that file does: `chitty add Idea -c backlog -s dropped` exits non-zero, its output contains `create the ticket, then drop it with chitty edit -s dropped --summary`, and no file is created in `chitty/backlog/` (fails before the change: `dropped` is not yet a valid `-s` choice, so the message is missing; after it, a check placed after the coercion would create a `backlog` ticket). For a `backlog` ticket there, `chitty edit <id> -s dropped --summary "x"` exits non-zero, its output contains `chitty move <id> tasks`, and the file is byte-identical (fails before the change on the missing message; it guards against adding `dropped` as an exception to the random-ID rule).
- `chitty summary`: a `dropped` ticket and a `done` ticket, both with History transitions in the window: in the output, `dropped (` comes before `done (` (the section headings `src/chitty/cli.py` prints).
- The model round-trips: for each status in `("dropped", *chitty.model.STATUSES)` (`dropped` named explicitly so the test fails before the change, and `STATUSES` iterated so a future status is covered), the text of a ticket written by `chitty add`, with its status line changed to that status, gives `chitty.model.parse(text).render() == text`. It fails before the change: `parse` validates the status through `Frontmatter.model_validate`, which rejects `dropped`.

Docs: the `- Statuses:` bullet in `docs/plan/task-file.md` (below the `## Frontmatter` table) and the `chitty --help` text for `-s`, if it lists statuses, name `dropped` and say what it is for. The role guides are a later ticket.

## Acceptance Criteria

- [ ] Edit rules: the `tests/test_status_dropped.py` cases for every allowed starting status and the refusal from `done` pass, each asserting its message, and fail before the change
- [ ] Revive, dependency, summary and round-trip: the `tests/test_status_dropped.py` cases for `-s todo` from `dropped`, the dependent `TASK-2` with its positive control, `chitty summary` and the per-status round trip pass, and fail before the change (some only because `dropped` cannot be parsed yet); the `- Statuses:` bullet in `docs/plan/task-file.md` lists `dropped` and says in one clause it is for tickets that will not be done, with a Summary saying why; `make check` passes. Record both runs in a note
- [ ] List and archive: the `tests/test_status_dropped.py` cases for `chitty list`, `-s dropped` and `--all`, `chitty archive` with no ID leaving the dropped ticket, and `chitty archive TASK-1` refused in both archive modes pass, and fail before the change. Record both runs in a note
- [ ] Summary rules: the `tests/test_status_dropped.py` cases for the summary refusals (none, `""`, whitespace, a whitespace-only Summary in the file), `-s dropped` and `--summary ""` on a dropped ticket, `--note` on a dropped ticket with no Summary, and the `chitty add T -d x -s dropped` refusal pass, each asserting its message, and fail before the change. Record both runs in a note
- [ ] Random-ID contexts: the `tests/test_status_dropped.py` cases for `chitty add -c backlog -s dropped` and `-s dropped` on a `backlog`-context ticket pass, each asserting its message and that nothing is written, and fail before the change

## Notes

Planner, 2026-11-23: the random-ID blocker is resolved by keeping that context rule unchanged (decided with the person; see the Description); added criterion 5. Earlier blockers were resolved on 2026-11-22 and 2026-11-23.

Planning blockers found before implementation:

1. The per-status round-trip test is required to iterate `chitty.model.STATUSES` and fail before the change because `dropped` cannot be parsed. But `src/chitty/model.py` does not include `dropped` in `STATUSES` before the change, so that test never attempts to parse it and cannot fail for the stated reason. Criterion 2 requires that failure. Specify an additional explicit `dropped` case or correct the before-change requirement while preserving future-status coverage.

2. The description requires `chitty add -s dropped` to produce the specified store error in every context, with the refusal located in `Repo.add` and nothing else changed. `src/chitty/cli.py:424` rejects a sequential-context add without a description before calling `Repo.add`; even after adding the status choice, the specified command cannot reach that refusal. Decide whether the CLI validation must change or the command/test must include a description, and reconcile the every-add requirement.

Inspected the status definitions, add and edit validation, selection and CLI list/summary paths, archive and dependency locations, and existing test fixture locations. No implementation or regression tests were written; before/after test runs and full verification remain outstanding pending clarification.

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
- 2026-11-23T12:23:32Z jolly-teal-quail: changed owner, notes
- 2026-11-23T12:23:32Z jolly-teal-quail doing → planning
- 2026-11-23T18:37:13Z witty-yellow-vole: replaced notes; changed owner, description, acceptance criteria
- 2026-11-23T18:37:29Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T18:37:29Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:39:54Z witty-yellow-vole: changed description
- 2026-11-23T18:39:54Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:40:13Z witty-yellow-vole: changed acceptance criteria; wrote the plan
- 2026-11-23T18:40:17Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:43:23Z witty-yellow-vole: changed description
- 2026-11-23T18:43:23Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:43:28Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:44:08Z witty-yellow-vole: changed description
- 2026-11-23T18:44:08Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:44:11Z witty-yellow-vole planning → todo
- 2026-11-23T18:56:06Z intrepid-dusky-gannet todo → doing
- 2026-11-23T18:59:50Z intrepid-dusky-gannet: changed owner, notes
- 2026-11-23T18:59:50Z intrepid-dusky-gannet doing → planning
- 2026-11-23T19:27:28Z witty-yellow-vole: changed owner, description
- 2026-11-23T19:28:09Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:36:59Z witty-yellow-vole: changed acceptance criteria
- 2026-11-23T19:36:59Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:37:01Z witty-yellow-vole planning → todo
- 2026-11-23T19:38:33Z daring-hazel-eel todo → doing
