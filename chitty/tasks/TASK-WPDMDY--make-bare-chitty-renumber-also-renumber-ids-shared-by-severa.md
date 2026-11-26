---
title: Make bare `chitty renumber` also renumber IDs shared by several files
status: todo
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

### Why

The person, 2026-11-26: renumbering should "renumber all the tickets that need it". Bare `chitty renumber` renumbers provisional tickets, but when two files share an ID (after a merge) it refuses with "used by more than one file" (`Repo._plan_provisional_renumbering`, `src/chitty/store.py`), and the person must find each file and run `chitty renumber <path>`.

### Change

Bare `chitty renumber` (`renumber` in `src/chitty/cli.py`; the logic in `Repo` in `src/chitty/store.py`) first checks the branch exactly as `_plan_provisional_renumbering` does, so off `main` it changes nothing for either step. Then:

1. For each group of files in one context (active and archived, as `Repo.renumber` finds `others`) sharing an ID, provisional files included, it calls the existing `Repo.renumber(path)` for every file but one. The file that keeps the ID has the earliest transition line in History (lines `HISTORY_LINE_RE` in `src/chitty/model.py` matches; a date-only line counts as midnight UTC that day; a file with none sorts last); ties go to the path that sorts first. Each call makes its own commit, as today; the command is not atomic across groups.
2. Then every provisional ticket, through the existing `renumber_provisional`. Step 1 runs first, so no provisional ID is shared by then.

Output: one `renumbered <old> -> <new> <path>` line per renumbered file, then each `check reference ...` line from step 1 once; `nothing to renumber` when there is nothing; with `--json`, a list of the renumbered tickets as bare `renumber --json` prints today. Update the command's help. The path form and the MCP `renumber` tool are unchanged.

### Out of scope

Renumbering when a branch lands (TASK-V4NQEM, which also changes the off-`main` rule); restarting numbering (TASK-W74AVC).

## Acceptance Criteria

- [ ] In `tests/test_renumber.py`, a new `CliTestCase` subclass (no Git, so numbering is sequential as on `main`) reuses a helper extracted from `TestRenumber.setUp` to make two files sharing `TASK-24`, rewrites their first History transition timestamps by hand so they differ, and adds one provisional ticket (`provisional: true` written into its file directly). Bare `chitty renumber` keeps `TASK-24` on the file with the earlier transition, gives the other file and the provisional ticket new numbers, prints one `renumbered <old> -> <new> <path>` line for each and each `check reference ...` line once; afterwards `chitty check` reports no `used by more than one file` problem. Fails without the change, because today bare `chitty renumber` refuses on the shared ID.
- [ ] In a Git repository on a branch other than `main`, bare `chitty renumber` with a shared ID changes nothing and prints the off-`main` message. Regression tests: the existing tests in `tests/test_renumber.py` and `tests/test_renumber_provisional.py` pass. `make check` passes.

## History

- 2026-11-26T17:49:33Z calm-ochre-quail → backlog
- 2026-11-26T17:49:46Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T17:49:46Z calm-ochre-quail backlog → todo
