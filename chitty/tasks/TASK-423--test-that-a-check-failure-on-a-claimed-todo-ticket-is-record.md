---
title: Test that a `check` failure on a claimed `todo` ticket is recorded on the ticket branch
status: doing
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

- Directly before `chitty run` (after the fake agent is installed), record `main_before = git rev-parse main`, stripped.
- After it: `git log --format=%s <main_before>..main -- <path>` prints exactly one line, `chitty: edit TASK-1 Todo` (the claim), so no other commit on `main` touched the ticket. Limit it to the ticket path: `main` also gains a `chitty: upgrade repository setup` commit during the run, because the fixture's config is older than `chitty init` writes.
- `git show task-1:<path>`, where `<path>` is the ticket path the test already computes, contains `status: error`, `Runner error (check)`, `check exited with status 1` and `check line 6`.

The existing assertions already check that `git show main:<path>` contains `status: doing`, that `task-1` is one commit ahead of `main`, that this commit changes only the ticket file, and that `check-args` is untracked in the worktree.

Evidence. The code exists, so show the test fails against a wrong version of `src/chitty/run.py`, made by hand and not committed: in `_handle_check_failure`, replace the last line with `return _record_ticket_error(Repo(git.main_checkout(branch_repo.root), branch_repo.config), action, "check", ChittyError(detail))`, which records the error through the main checkout. Run the test, record in a note which assertion fails first (expected: the existing `status: doing` check on `main`), then restore the file.

No property: one fixed scenario; the behaviour drives real Git and runner processes. The `check` failure on a `doing` ticket (`test_run_check_failure_on_doing_ticket_starts_agent`) wrote its note through the worktree before `TASK-382` too, so it is unchanged and out of scope.

## Acceptance Criteria

- [ ] `test_run_check_failure_on_todo_ticket_records_error_on_branch` exists in place of the old name and passes with every existing and added assertion listed in the Description
- [ ] A note records the assertion that fails first against the wrong version of `run.py` described under Evidence; `make check` passes

## Plan

Strengthen the existing TestNext regression test only: rename it, capture main before chitty run, assert main has only the ticket claim commit, and inspect the branch ticket error contents. First run the requested wrong-run.py experiment and record which assertion fails first; restore run.py immediately. Then run the focused test and make check, commit test changes with Task: TASK-423, record verification and summary, and move the ticket to review.

## History

- 2026-11-19T13:29:53Z quick-ginger-lapwing → backlog
- 2026-11-19T13:39:57Z quick-ginger-lapwing: changed priority, description, acceptance criteria
- 2026-11-19T13:39:57Z quick-ginger-lapwing backlog → planning
- 2026-11-19T13:40:02Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T13:41:38Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T13:41:43Z quick-ginger-lapwing: changed description
- 2026-11-19T13:41:47Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T13:43:03Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T13:43:06Z quick-ginger-lapwing: changed description
- 2026-11-19T13:43:06Z quick-ginger-lapwing planning → todo
- 2026-11-19T14:36:29Z able-jade-urchin todo → doing
- 2026-11-19T14:37:24Z able-jade-urchin: wrote the plan
