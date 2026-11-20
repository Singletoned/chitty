---
title: Do not error a `todo` ticket whose branch already has work when the pre-session check fails
status: doing
created: 2026-11-20
---

## Description

The runner runs the configured `check` before each work session. When it fails, `_handle_check_failure` in `src/chitty/run.py` starts the agent anyway for a `doing` or `error` ticket, with a `Check failed before this session` note, but sends a `todo` ticket to `error` with no agent. That is right for a fresh `todo` ticket: a failing check there means `main` itself is broken. It is wrong for a `todo` ticket whose branch already holds work from an earlier session, because the failing check is usually that unfinished work. It happened twice on 2026-11-20: `TASK-474` after a planner settled a worker question, and `TASK-479` after it was re-planned over its worker's partial implementation. Both times a person had to move the ticket to `doing` by hand. Decided with the owner 2026-11-20: fix it in the runner, not with a guide rule.

Decisions:

- A pure function `_has_work(paths: Sequence[PurePosixPath]) -> bool` in `src/chitty/run.py`: true exactly when some path is not inside the `chitty/` directory, that is, does not have at least two parts with the first equal to `BACKLOG_DIR` (`chitty`, from `src/chitty/config.py`). So `chitty.toml`, `AGENTS.md`, a file named exactly `chitty`, and `chitty-notes/x` are work; `chitty/tasks/TASK-1--x.md` is not. `_branch_has_work(worktree: Path, main_branch: str) -> bool` returns `_has_work(git.changed_paths(worktree, main_branch, "HEAD"))` (`src/chitty/git.py`, committed changes since the merge base). Add the `NotImplementedError` stub of `_has_work` first, so the property fails on behaviour. Changes to ticket files alone are not work: the runner's own claim (`todo` to `doing`, committed on the branch before the check runs) and planning notes only change `chitty/`.
- In `_handle_check_failure`, the agent starts when `action.mode == "work"`, `exited` is true, and either `selected_status` is `doing` or `error`, as today, or `selected_status` is `todo` and `_branch_has_work(branch_repo.root, branch_repo.config.main_branch)`. `branch_repo.root` is the ticket worktree there. Everything else is unchanged: the note text, and `error` for a missing check command (`exited` false) and for a `todo` ticket without work.
- The caller's `todo` handling after `_run_check` (in the session code, `if action.mode == "work" and selected_status == "todo": return RunResult(...)`) only runs when `_run_check` returns a failure, so it needs no change.
- Docs: in `docs/plan/next-action-and-runner.md`, the work-mode bullet that says a check failure on a `doing` or `error` ticket appends `Check failed before this session` (about line 128): add that a `todo` ticket whose branch changes files outside `chitty/` is treated the same way, and change the next sentence (about lines 130 and 131), which says a `todo` ticket moves to `error`, so that it begins: On a `todo` ticket without work outside `chitty/`, or when the `check` command is not found.
- `TASK-353` changes the same check-failure path to write output to a log instead of the note; whichever lands second rebases onto the other. Nothing here depends on the note's content.

Tests: in `tests/test_next.py`, next to `test_run_check_failure_on_doing_ticket_starts_agent` and using the same helpers (`write_failing_checker`, `commit_ticket`, `install_fake_pi`):

- `test_run_check_failure_on_todo_ticket_with_work_starts_agent`: `write_failing_checker()`, `commit_ticket("Todo", "todo")`, `self.git("switch", "-c", "task-1")`, write and commit `work.py`, `self.git("switch", "main")`. The fake agent is the one in `test_run_check_failure_on_doing_ticket_starts_agent` (it records the ticket it sees, then sets `status: review` and commits).
- `test_run_check_failure_on_todo_ticket_with_only_ticket_commits_errors`: the same, but on `task-1` the commit appends a line to the ticket's Notes section in its file under `chitty/tasks/` instead of adding `work.py`. The fake agent only writes the marker file `self.tmp / "agent-started"` (outside the repository; `RepoTestCase` makes `self.tmp`). Assert the ticket ends `error` and the marker does not exist.

Property in a new `tests/test_property_branch_work.py` with Hypothesis: generate lists of zero or more paths, each built as either a ticket path `chitty/<segment>/.../<file>` (two or more parts) or a work path drawn from `chitty.toml`, `chitty` alone, `chitty-notes/<rest>`, `x/chitty/<rest>`, `AGENTS.md` or `src/<rest>`, with segments from letters, digits, `-`, `.` and `é`. `_has_work` is true exactly when some drawn path was built as a work path, and the order of the list does not matter. The two runner tests stay as integration checks, with the existing fresh-`todo` test as the third branch state.

## Acceptance Criteria

- [ ] In `tests/test_next.py`, a `todo` ticket whose branch `task-1` has a commit adding `work.py` gets an agent despite a failing check: `chitty run` prints `TASK-1: doing → review`, and the ticket the agent sees contains `Check failed before this session`; fails before the change (the ticket goes to `error` and no agent starts)
- [ ] A `todo` ticket whose branch has only a commit changing its own ticket file still goes to `error` with no agent started (the fake agent's marker file is absent), and `test_run_check_failure_on_todo_ticket_records_error_on_branch` passes unchanged; both are guards that pass before the change
- [ ] `docs/plan/next-action-and-runner.md` states the new rule where it describes check failures, and `make check` passes
- [ ] The `_has_work` property in `tests/test_property_branch_work.py` passes; a note records that it fails while `_has_work` raises `NotImplementedError` and against a mutant using `str(path).startswith("chitty")`

## Plan

Add integration and property regressions, demonstrate failures against the stub and prefix mutant, then implement merge-base path detection and update runner documentation. Run formatting and checks before handoff.

## Notes

Suggestion origin: chitty

Before the fix, the work-branch integration test failed with todo to error; both ticket-only and fresh-todo guards passed. The property failed with NotImplementedError and rejected the startswith prefix mutant with chitty.toml.

## Summary

Runner now starts the work agent after a failing check on a todo branch with committed changes outside chitty; ticket-only branches still error. Added integration and property regressions and updated runner documentation. Verified make check (866 tests) and the pre-fix failures noted above. No follow-ups.

## History

- 2026-11-20T23:09:59Z quick-pearl-lapwing → backlog
- 2026-11-20T23:11:52Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:11:52Z quick-pearl-lapwing backlog → planning
- 2026-11-20T23:11:58Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:13:05Z quick-pearl-lapwing: changed description, acceptance criteria
- 2026-11-20T23:13:05Z quick-pearl-lapwing cold-read → todo
- 2026-11-20T23:13:23Z quick-pearl-lapwing: changed description
- 2026-11-20T23:13:38Z nimble-fawn-vole todo → doing
- 2026-11-20T23:15:34Z nimble-fawn-vole: wrote the plan
- 2026-11-20T23:16:31Z nimble-fawn-vole: changed notes
- 2026-11-20T23:18:42Z nimble-fawn-vole: changed summary
