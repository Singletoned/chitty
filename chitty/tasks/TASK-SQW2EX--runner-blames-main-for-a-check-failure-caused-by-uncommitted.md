---
title: Runner blames main for a check failure caused by uncommitted edits in the ticket worktree
status: backlog
created: 2026-11-25
provisional: true
---

## Description

On 2026-11-24 `chitty run` set `TASK-651` to `error` with the note "Runner error (check): check exited with status 2; output in `.chitty/check.log`; the branch has no work yet, so `main` fails this check".

That was wrong. `main` passes: `tests/test_next.py::TestNext::test_run_review_compares_only_tool_chitty_in_pyproject` passes in the main checkout. The worktree `.worktrees/task-651` held a previous worker's uncommitted edits to `src/chitty/store.py`, `tests/test_cli.py`, `tests/test_next.py` and `tests/test_pi_retirement.py`, and the check ran against them. The branch had no implementation commits, so the runner decided the failure was on `main`.

Suggested fix: before running the pre-session check, look at `git status` in the worktree. If it is dirty, say so in the error ("the worktree has uncommitted changes to ...; they may cause this failure") instead of blaming `main`, or run the check against `HEAD` without the uncommitted changes. Related: workers that return a ticket leave uncommitted partial work in the worktree (see the suggestion "Workers return tickets to planning while noting the ticket has no defect").

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:27Z calm-ochre-quail → backlog
- 2026-11-25T22:28:28Z calm-ochre-quail: changed notes
