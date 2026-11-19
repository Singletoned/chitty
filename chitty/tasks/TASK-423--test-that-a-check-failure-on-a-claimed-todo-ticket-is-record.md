---
title: Test that a `check` failure on a claimed `todo` ticket is recorded on the ticket branch
status: cold-read
priority: high
depends_on:
  - TASK-382
parent: TASK-376
created: 2026-11-19
---

## Description

`TASK-382` makes the runner record a failing `check` as an error on the ticket branch instead of `main`. When the runner picks a `todo` ticket, it first commits the claim (`todo → doing`) on `main`, then creates the branch and runs `check` there. The test for this case on the `TASK-382` branch does not check where the error was committed, or that `main` gained only the claim. This ticket strengthens it; it changes tests only. Split from `TASK-382` on 2026-11-19.

In `tests/test_next.py`, class `TestNext`, rename `test_run_check_failure_records_output_and_does_not_claim_or_start_agent` to `test_run_check_failure_on_todo_ticket_records_error_on_branch` (it does claim). Keep its fixture and action: the check script `check.py` records its arguments and the ticket, prints `check line 1` to `check line 25`, and exits 1; config `autocommit = true` and `setup = "true"`; a Git repository on `main` with ticket `TASK-1` titled `Todo` committed as `setup`; a fake agent that would write `started`; then `chitty run`. Keep every existing assertion.

Add:

- Before `chitty run`, record `main_before = git rev-parse main`.
- After it: `git log --format=%s <main_before>..main` prints exactly one line, `chitty: edit TASK-1 Todo` (the claim).
- `git show task-1:<path>`, where `<path>` is the ticket path the test already computes, contains `status: error`, `Runner error (check)`, `check exited with status 1` and `check line 6`.

The existing assertions already check that `git show main:<path>` contains `status: doing`, that `task-1` is one commit ahead of `main`, that this commit changes only the ticket file, and that `check-args` is untracked in the worktree.

Evidence. The code exists, so show the test fails against a wrong version of `src/chitty/run.py`, made by hand and not committed: in `_handle_check_failure`, replace the last line with `return _record_ticket_error(Repo(git.main_checkout(branch_repo.root), branch_repo.config), action, "check", ChittyError(detail))`, which records the error through the main checkout. Run the test, record in a note which assertion fails first, then restore the file.

No property: one fixed scenario; the behaviour drives real Git and runner processes. The `check` failure on a `doing` ticket (`test_run_check_failure_on_doing_ticket_starts_agent`) wrote its note through the worktree before `TASK-382` too, so it is unchanged and out of scope.

## Acceptance Criteria

- [ ] `test_run_check_failure_on_todo_ticket_records_error_on_branch` exists in place of the old name and passes with every existing and added assertion listed in the Description
- [ ] A note records the assertion that fails first against the wrong version of `run.py` described under Evidence; `make check` passes

## History

- 2026-11-19T13:29:53Z quick-ginger-lapwing → backlog
- 2026-11-19T13:39:57Z quick-ginger-lapwing: changed priority, description, acceptance criteria
- 2026-11-19T13:39:57Z quick-ginger-lapwing backlog → planning
- 2026-11-19T13:40:02Z quick-ginger-lapwing planning → cold-read
