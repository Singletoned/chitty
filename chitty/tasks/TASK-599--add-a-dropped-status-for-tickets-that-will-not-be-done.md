---
title: Add a `dropped` status for tickets that will not be done
status: doing
labels:
  - needs-minor
priority: high
created: 2026-11-22
---

## Description

Decided with the person, 2026-11-22: there must be a quick, honest way to kill a ticket. Today the only way to close one is `done`, which with review on needs `-s review` first, so closing a ticket nobody will build means pretending it was reviewed. This ticket adds the status only; `TASK-652`, `TASK-653` and `TASK-654` add its rules.

Change, in `src/chitty/model.py`:

- Append `dropped` to `STATUSES` and to the frontmatter `status` `Literal` (around line 177).
- `STATUS_GLYPHS["dropped"] = "🚫"` and `STATUS_LABELS["dropped"] = "drop"`. Leave `DEFAULT_LIST_STATUSES` alone, so `chitty list` hides dropped tickets as it hides `done`.
- Nothing else. `chitty edit <id> -s dropped` then works from any status with no extra rules, because the `-s` choices come from `STATUSES`. The runner never selects a dropped ticket, and a dependency on one stays unmet, because only `done` or archived satisfies a dependency (`_dependency_is_done` in `src/chitty/store.py`). Do not change either. The MCP `Status` type is `TASK-601`.

Docs: the `- Statuses:` bullet in `docs/plan/task-file.md` names `dropped`, for tickets that will not be done.

Tests, in a new `tests/test_status_dropped.py`, with classes inheriting `CliTestCase` from `tests/test_cli.py` (no Git repository needed). Write any ticket in a non-default status straight into its file's frontmatter:

- `chitty edit TASK-1 -s dropped` on a `todo` ticket exits 0, and the file has `status: dropped`. Then `-s todo` exits 0.
- With a dropped ticket whose title contains neither `drop` nor `done`, `chitty list` does not show its ID, and `chitty list -s dropped` shows it with `🚫` and `drop`.
- Round trip: for each status in `("dropped", *chitty.model.STATUSES)`, a ticket file written by `chitty add` with its status line changed to that status satisfies `parse(text).render() == text`.
- Regression test: `TASK-2` in `todo` with `depends_on: [TASK-1]`, where `TASK-1` is `dropped`, plus an independent `todo` `TASK-3`: `chitty next --mode work` prints `work TASK-3`.

`chitty summary` will list a `dropped` section before `done` (it ranks `reversed` statuses); that is intended. Before the change, the list and dependency fixtures fail at parsing, which is enough.

Out of scope: rules for dropping, `chitty add -s dropped`, archiving, and the guides.

## Acceptance Criteria

- [ ] The `tests/test_status_dropped.py` cases for `-s dropped`, `-s todo` from `dropped`, `chitty list` and the round trip pass, and each fails before the change (record the run in a note); the dependency regression test passes
- [ ] The `- Statuses:` bullet in `docs/plan/task-file.md` names `dropped`; `make check` passes

## Plan

Add focused CLI and round-trip tests and confirm they fail before adding the status; then update the model and task-file design, run formatting and checks, and submit for review.

## Notes

Narrowed 2026-11-26 after four stalled runs: the `chitty summary` test was cut (its order follows from `STATUSES`), the dependency check is now a regression test, and the close-from-`main` request moved to TASK-10036.

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
- 2026-11-24T09:30:16Z rosy-russet-wren: changed owner, notes
- 2026-11-24T09:30:16Z rosy-russet-wren doing → planning
- 2026-11-25T20:44:38Z golden-coral-stoat: changed notes
- 2026-11-26T11:38:45Z brisk-bronze-adder: changed notes
- 2026-11-26T11:38:45Z brisk-bronze-adder planning → to-plan
- 2026-11-26T11:38:52Z brisk-bronze-adder to-plan → planning
- 2026-11-26T11:39:00Z brisk-bronze-adder: replaced notes; changed owner, description, acceptance criteria; wrote the plan
- 2026-11-26T11:39:00Z brisk-bronze-adder planning → cold-read
- 2026-11-26T12:03:37Z brisk-bronze-adder cold-read → planning
- 2026-11-26T12:03:45Z brisk-bronze-adder: changed description
- 2026-11-26T12:03:45Z brisk-bronze-adder planning → todo
- 2026-11-26T12:28:23Z zesty-indigo-vole todo → doing
- 2026-11-26T12:32:32Z zesty-indigo-vole: wrote the plan
