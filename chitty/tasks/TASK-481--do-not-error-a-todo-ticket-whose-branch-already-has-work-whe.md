---
title: Do not error a `todo` ticket whose branch already has work when the pre-session check fails
status: planning
created: 2026-11-20
---

## Description

The runner runs the configured `check` before each work session. When it fails, `_handle_check_failure` in `src/chitty/run.py` starts the agent anyway for a `doing` or `error` ticket, with a `Check failed before this session` note, but sends a `todo` ticket to `error` with no agent. That is right for a fresh `todo` ticket: a failing check there means `main` itself is broken. It is wrong for a `todo` ticket whose branch already holds work from an earlier session, because the failing check is usually that unfinished work. It happened twice on 2026-11-20: `TASK-474` after a planner settled a worker question, and `TASK-479` after it was re-planned over its worker's partial implementation. Both times a person had to move the ticket to `doing` by hand. Decided with the owner 2026-11-20: fix it in the runner, not with a guide rule.

Decisions:

- A new function `_branch_has_work(worktree: Path, main_branch: str) -> bool` in `src/chitty/run.py`: true when any path in `git.changed_paths(worktree, main_branch, "HEAD")` (`src/chitty/git.py`, committed changes since the merge base) has a first part other than `BACKLOG_DIR` (`chitty`, from `src/chitty/config.py`). Changes to ticket files alone are not work: the runner's own claim (`todo` to `doing`, committed on the branch before the check runs) and planning notes only change `chitty/`.
- In `_handle_check_failure`, the agent starts when `action.mode == "work"`, `exited` is true, and either `selected_status` is `doing` or `error`, as today, or `selected_status` is `todo` and `_branch_has_work(branch_repo.root, branch_repo.config.main_branch)`. `branch_repo.root` is the ticket worktree there. Everything else is unchanged: the note text, and `error` for a missing check command (`exited` false) and for a `todo` ticket without work.
- The caller's `todo` handling after `_run_check` (in the session code, `if action.mode == "work" and selected_status == "todo": return RunResult(...)`) only runs when `_run_check` returns a failure, so it needs no change.
- Docs: in `docs/plan/next-action-and-runner.md`, the work-mode bullet that says a check failure on a `doing` or `error` ticket appends `Check failed before this session` (about line 128): add that a `todo` ticket whose branch changes files outside `chitty/` is treated the same way.
- `TASK-353` changes the same check-failure path to write output to a log instead of the note; whichever lands second rebases onto the other. Nothing here depends on the note's content.

Tests: in `tests/test_next.py`, next to `test_run_check_failure_on_doing_ticket_starts_agent` and using the same helpers (`write_failing_checker`, `commit_ticket`, `install_fake_pi`):

- `test_run_check_failure_on_todo_ticket_with_work_starts_agent`: `write_failing_checker()`, `commit_ticket("Todo", "todo")`, `git switch -c task-1`, write and commit `work.py`, `git switch main`. The fake agent is the one in `test_run_check_failure_on_doing_ticket_starts_agent` (it records the ticket it sees, then sets `status: review` and commits).
- `test_run_check_failure_on_todo_ticket_with_only_ticket_commits_errors`: the same, but on `task-1` the commit appends a line to the ticket's Notes section in its file under `chitty/tasks/` instead of adding `work.py`. The fake agent only writes a marker file outside the repository. Assert the ticket ends `error` and the marker does not exist.

No property: two fixed branch states, plus the existing fresh-`todo` test as the third.

## Acceptance Criteria

- [ ] In `tests/test_next.py`, a `todo` ticket whose branch `task-1` has a commit adding `work.py` gets an agent despite a failing check: `chitty run` prints `TASK-1: doing → review`, and the ticket the agent sees contains `Check failed before this session`; fails before the change (the ticket goes to `error` and no agent starts)
- [ ] A `todo` ticket whose branch has only a commit changing its own ticket file still goes to `error` with no agent started (the fake agent's marker file is absent), and `test_run_check_failure_on_todo_ticket_records_error_on_branch` passes unchanged; both are guards that pass before the change
- [ ] `docs/plan/next-action-and-runner.md` states the new rule where it describes check failures, and `make check` passes

## Notes

Suggestion origin: chitty

## History

- 2026-11-20T23:09:59Z quick-pearl-lapwing → backlog
- 2026-11-20T23:11:52Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:11:52Z quick-pearl-lapwing backlog → planning
