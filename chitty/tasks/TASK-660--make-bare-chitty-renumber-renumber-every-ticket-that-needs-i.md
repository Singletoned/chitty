---
title: Make bare `chitty renumber` renumber every ticket that needs it
status: cold-read
labels:
  - bug
created: 2026-11-24
---

## Description

### Why

In echonomicon on 2026-11-24, after a plan branch landed, `chitty renumber chitty/tasks/TASK-BCHE6A--*.md` failed with "TASK-BCHE6A is used by no other file; use `chitty move` to give it a new ID", and `chitty move TASK-BCHE6A tasks` also failed, so the planner kept the provisional IDs. Bare `chitty renumber` would have worked, but nothing said so, and it refuses outright when two files share an ID. Decided (the person, 2026-11-26): one command renumbers all the tickets that need it.

### Change

Bare `chitty renumber` (`renumber` in `src/chitty/cli.py`, and `Repo` in `src/chitty/store.py`) on `main` (or outside Git) renumbers, in this order:

1. Every file but one in each group of files sharing an ID, by calling the existing `Repo.renumber(path)` for each, which allocates the next number and lists the tickets naming the old ID (references to a shared ID are not rewritten, as today). The file that keeps the ID is the one whose first History entry is earliest: compare the entries' timestamps, with a date-only entry counting as the start of that day; on a tie, the path that sorts first keeps it.
2. Then every provisional ticket, through the existing `renumber_provisional`.

It prints the same lines as the path form and the provisional form today, and `nothing to renumber` when there is nothing. Off `main` it keeps today's message and changes nothing. The path form keeps its behaviour for shared IDs; for a ticket whose ID no other file uses, its error becomes ``<ID> is used by no other file; run `chitty renumber` with no path``, since `chitty move` cannot renumber within a context. Update the command's help to match. The MCP `renumber` tool keeps taking a path.

### Out of scope

Renumbering when a branch lands (TASK-V4NQEM); restarting numbering (TASK-W74AVC); renumbering a numbered ticket with a unique ID.

## Acceptance Criteria

- [ ] In `tests/test_renumber.py`, a new `CliTestCase` subclass (no Git, so numbers are sequential as on `main`) sets up two files sharing `TASK-24` (as `TestRenumber.setUp` does) whose first History entries differ, plus one provisional ticket (`provisional: true` written into its file directly). Bare `chitty renumber` keeps `TASK-24` on the file with the earlier first History entry, gives the other file and the provisional ticket new numbers, prints one `renumbered <old> -> <new> <path>` line for each and a `check reference ...` line for each ticket naming `TASK-24`; afterwards `chitty check` reports no `used by more than one file` problem. Fails without the change, because today bare `chitty renumber` refuses on the shared ID.
- [ ] Bare `chitty renumber` with only shared IDs (no provisional tickets) renumbers them the same way; `chitty renumber <path>` for a ticket whose ID no other file uses exits 1 with `is used by no other file; run chitty renumber with no path` and changes nothing. Regression tests: the existing tests in `tests/test_renumber.py` (with that message updated) and `tests/test_renumber_provisional.py` pass. `make check` passes.

## Plan

Extend the existing provisional renumber planner and execution to accept explicit candidates, route unique IDs through it, and retain duplicate-ID behavior. Add CLI and preflight regression tests, verify they fail before the fix, then run formatting and checks.

## Notes

Before the fix, the unique numbered and provisional CLI cases fail with the no-other-file error; the feature-branch case fails because it reports that error instead of ProvisionalOffMain.

Reviewed: Complete diff inspected; checks pass.
1: pass - make check passes; in a merge-base worktree, PYTHONPATH=<worktree>/src:<worktree> pytest tests/test_renumber.py::TestRenumberUnique failed both numbered and provisional subtests with the old no-other-file error, and the random-context test failed on the old error.
2: pass - make check passes (1247 tests); the merge-base pytest test_unique_numbered_ticket_on_feature_branch failed because the old no-other-file error replaced the required off-main message. Regression tests pass in make check.

## Summary

Unique sequential-context tickets now renumber through the existing reference-rewriting planner; shared IDs retain their existing behavior. Verified failing tests before the fix, targeted regression tests, and make check (1243 passed).

## History

- 2026-11-24T22:21:23Z zesty-coral-newt → backlog
- 2026-11-24T22:21:24Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:36Z zesty-coral-newt: changed labels
- 2026-11-26T11:11:51Z calm-ochre-quail: changed title, notes
- 2026-11-26T11:11:51Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:20:40Z calm-ochre-quail: replaced notes; changed dependencies, description, acceptance criteria
- 2026-11-26T11:20:40Z calm-ochre-quail to-plan → cold-read
- 2026-11-26T11:20:52Z calm-ochre-quail: changed acceptance criteria
- 2026-11-26T11:22:30Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T11:22:30Z calm-ochre-quail cold-read → todo
- 2026-11-26T11:55:31Z zesty-zinc-puffin todo → doing
- 2026-11-26T11:59:52Z zesty-zinc-puffin: wrote the plan
- 2026-11-26T12:00:46Z zesty-zinc-puffin: changed notes
- 2026-11-26T12:08:41Z zesty-zinc-puffin: changed summary; ticked acceptance criteria
- 2026-11-26T12:11:02Z zesty-zinc-puffin doing → review
- 2026-11-26T12:17:42Z mellow-silver-crane: changed notes
- 2026-11-26T12:17:42Z mellow-silver-crane review → done
- 2026-11-26T17:46:58Z calm-ochre-quail: changed title, dependencies, description, acceptance criteria
- 2026-11-26T17:46:58Z calm-ochre-quail done → cold-read
- 2026-11-26T17:47:10Z calm-ochre-quail: changed description
