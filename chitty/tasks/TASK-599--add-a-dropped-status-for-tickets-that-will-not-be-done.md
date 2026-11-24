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

Split on 2026-11-24 into this ticket (the status) and three that depend on it: `TASK-652` (dropping needs a Summary; `done` cannot be dropped), `TASK-653` (`chitty add -s dropped` refused; random-ID contexts) and `TASK-654` (archive refuses a dropped ticket).

Decisions:

- New status `dropped`, last in `STATUSES` in `src/chitty/model.py`, and in the frontmatter `status` `Literal` (`src/chitty/model.py`, around line 172). The MCP `Status` `Literal` (`src/chitty/mcp.py`) is `TASK-601`; until it lands, MCP `list` with `all` (which uses `STATUSES`) returns dropped tickets while MCP edits cannot set `dropped`, which is acceptable. Glyph `🚫` (U+1F6AB, an emoji-presentation character, so it needs no variation selector) in `STATUS_GLYPHS`; label `drop` in `STATUS_LABELS`. Not in `DEFAULT_LIST_STATUSES`, so `chitty list` hides it as it hides `done`; `chitty list -s dropped` and `--all` show it.
- In this ticket `chitty edit <id> -s dropped` works like any other status change, from any status and with no Summary required; `TASK-652` adds those rules. `chitty add -s dropped` and `chitty archive <id>` on a dropped ticket are not changed here (`TASK-653`, `TASK-654`).
- `chitty summary`: appending `dropped` to `STATUSES` makes `summarize` (which ranks `reversed(TASK_STATUSES)`) list a `dropped` section before `done`; keep that, as both are final.
- Nothing else changes in this ticket: the runner selects only `todo` and `doing` to work and `review` to review (`src/chitty/selection.py`), so it never picks a dropped ticket. A ticket that depends on a dropped ticket stays blocked, since only `done` or archived satisfies a dependency (`src/chitty/store.py`, `_dependency_is_done` and the function after it, which test `archived` or `status == "done"`); an implementation that counted `dropped` as satisfied would be wrong; how dependents and release labels treat `dropped` is a later ticket.
- The ticket's branch and worktree, if any, are not touched; the clean-up rule in `AGENTS.md` covers them. Editing a ticket whose latest copy is on a branch is still refused from the main checkout, as for any edit (`TASK-385` covers that).

Tests in a new `tests/test_status_dropped.py`, inheriting `CliTestCase` from `tests/test_cli.py` (a `RepoTestCase` whose `run_cli` wraps `click.testing.CliRunner`), as `tests/test_edit_human.py` does; the repository is not a Git repository (no `git init`), so dependencies read the working files, in the `RepoTestCase` repository (`tests/support.py` `CONFIG`: `workflow = "runner"`, so review is on, and `archive` is the default `"move"`). Every `done` ticket in a fixture is written directly with `status: done` in its frontmatter, since review is on and `chitty add -s done` is refused:

- `chitty edit TASK-1 -s dropped` on a `todo` ticket exits 0 and the file has `status: dropped` (fails before the change: `dropped` is not a valid `-s` choice).
- For the list cases, write the `dropped` ticket file directly in the fixture (`status: dropped` in its frontmatter), since before the change the CLI cannot make one. Give the dropped ticket a title containing neither `drop` nor `done`, and assert on its ID: `chitty list` output does not contain it; `chitty list -s dropped` and `chitty list --all` do, with `🚫` and `drop`.
- `chitty edit TASK-1 -s todo` from `dropped` exits 0.
- A `todo` ticket `TASK-2` with `depends_on: [TASK-1]`, where `TASK-1` is `dropped`, plus an independent `todo` ticket `TASK-3`: `chitty next --mode work` exits 0 and prints `work TASK-3` (guards the unchanged dependency rule). Positive control: the same fixture without `TASK-3` and with `TASK-1` `done` prints `work TASK-2`.
- `chitty summary`: a `dropped` ticket and a `done` ticket, both with History transitions in the window: in the output, `dropped (` comes before `done (` (the section headings `src/chitty/cli.py` prints).
- The model round-trips: for each status in `("dropped", *chitty.model.STATUSES)` (`dropped` named explicitly so the test fails before the change, and `STATUSES` iterated so a future status is covered), the text of a ticket written by `chitty add`, with its status line changed to that status, gives `chitty.model.parse(text).render() == text`. It fails before the change: `parse` validates the status through `Frontmatter.model_validate`, which rejects `dropped`.

Docs: the `- Statuses:` bullet in `docs/plan/task-file.md` (below the `## Frontmatter` table) names `dropped` and says what it is for. No `--help` text changes: the `-s` choices come from `STATUSES`, and the `list -s` help lists only the defaults, which do not change. The role guides are a later ticket.

## Acceptance Criteria

- [ ] The `tests/test_status_dropped.py` cases for `-s dropped` on a `todo` ticket, `-s todo` from `dropped`, the per-status round trip and `chitty list` (hidden by default; shown by `-s dropped` and `--all` with `🚫` and `drop`) pass, and fail before the change. Record both runs in a note
- [ ] The dependent `TASK-2` case and its positive control, and the `chitty summary` order case, pass; the dependent case fails before the change only because `dropped` cannot be parsed, and against the wrong version where `dropped` satisfies a dependency. Record the runs in a note
- [ ] The `- Statuses:` bullet in `docs/plan/task-file.md` lists `dropped` and says in one clause it is for tickets that will not be done; `make check` passes

## Plan

Add dropped status definitions and docs; write the specified regression tests and verify they fail before implementation, then format, run make check, and record evidence.

## Notes

Planner, 2026-11-23: the random-ID blocker is resolved by keeping that context rule unchanged (decided with the person; see the Description); added criterion 5. Earlier blockers were resolved on 2026-11-22 and 2026-11-23.

Planning blockers found before implementation:

1. The per-status round-trip test is required to iterate `chitty.model.STATUSES` and fail before the change because `dropped` cannot be parsed. But `src/chitty/model.py` does not include `dropped` in `STATUSES` before the change, so that test never attempts to parse it and cannot fail for the stated reason. Criterion 2 requires that failure. Specify an additional explicit `dropped` case or correct the before-change requirement while preserving future-status coverage.

2. The description requires `chitty add -s dropped` to produce the specified store error in every context, with the refusal located in `Repo.add` and nothing else changed. `src/chitty/cli.py:424` rejects a sequential-context add without a description before calling `Repo.add`; even after adding the status choice, the specified command cannot reach that refusal. Decide whether the CLI validation must change or the command/test must include a description, and reconcile the every-add requirement.

Inspected the status definitions, add and edit validation, selection and CLI list/summary paths, archive and dependency locations, and existing test fixture locations. No implementation or regression tests were written; before/after test runs and full verification remain outstanding pending clarification.

Started investigation and recorded an approach. No implementation or regression tests written; before/after verification and make check remain outstanding.

Investigation continued: checked edit application and existing status validation. No code or tests have been changed; implementation and all verification remain outstanding.

Runner error (agent): TASK-599 is still `doing` after 5 continuations with no new work committed; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-599`

Error output:

```text
last session: exit 0 after 11s
I have not completed TASK-599. It remains in `doing`; I cannot honestly classify it as ready for review, defective, or externally blocked.
```

Requeued 2026-11-23: the stall ran on `gpt-6.1-terra` (Pi session logs), before `work_model = "openai-codex/gpt-6-luna"` landed in `chitty.toml` (`0ce50010`). The branch has no code yet.

Planning blockers confirmed by the ticket text and CLI behavior. The Description explicitly resolves both previously reported issues: round-trip test must include `dropped` explicitly (`("dropped", *STATUSES)`), and sequential `chitty add` without `-d` retains today's usage error; add tests use `-d x`. These are no longer blockers. However, task requires before-change test evidence for a large matrix, implementation, docs, and make check; it is doable, so proceed rather than planning. This status change is not appropriate; restoring doing.

Planning blocker: Acceptance criterion 1 requires the allowed-starting-status cases to “each assert[] their message,” but the Description specifies only their successful result (status, Summary, History), not any required success message. The `chitty edit` contract may return no success message, so this assertion is not verifiable as written. Please change the criterion to require the specified state assertions for successful cases and message assertions only for the refusal from `done`, or define the exact success message and evidence expected. I have not implemented code or tests.

Planner, 2026-11-24: split. The latest blocker (success cases cannot assert a message) is resolved by the rewrite: success cases assert state only. The ticket was also too large for one session (three stalled runs), so the edit rules, the `add` refusal and the archive refusal moved to `TASK-652`, `TASK-653` and `TASK-654`, which depend on this one.

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
- 2026-11-23T19:41:06Z daring-hazel-eel: wrote the plan
- 2026-11-23T19:41:18Z daring-hazel-eel: changed notes
- 2026-11-23T19:42:04Z daring-hazel-eel: changed notes
- 2026-11-23T19:43:01Z daring-hazel-eel: changed notes
- 2026-11-23T19:43:01Z daring-hazel-eel doing → error
- 2026-11-23T23:08:17Z friendly-coral-badger: changed notes
- 2026-11-23T23:08:17Z friendly-coral-badger error → todo
- 2026-11-23T23:13:28Z friendly-khaki-lapwing todo → doing
- 2026-11-23T23:16:56Z friendly-khaki-lapwing: changed owner, notes
- 2026-11-23T23:16:56Z friendly-khaki-lapwing doing → planning
- 2026-11-23T23:17:06Z friendly-khaki-lapwing: changed notes
- 2026-11-24T08:45:46Z sunny-hazel-gannet: changed title, description, acceptance criteria, notes
- 2026-11-24T08:45:46Z sunny-hazel-gannet planning → cold-read
- 2026-11-24T09:24:02Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T09:24:14Z sunny-hazel-gannet cold-read → planning
- 2026-11-24T09:24:19Z sunny-hazel-gannet planning → todo
- 2026-11-24T09:27:35Z rosy-russet-wren todo → doing
- 2026-11-24T09:29:47Z rosy-russet-wren: wrote the plan
