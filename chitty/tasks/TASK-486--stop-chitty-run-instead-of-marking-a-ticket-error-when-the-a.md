---
title: Stop `chitty run` instead of marking a ticket `error` when the agent fails before committing
status: doing
labels:
  - bug
priority: high
created: 2026-11-21
---

## Description

On 2026-11-20 a work loop was started as `chitty run --loop --mode work -- --model gpt-6.2-terra`, a model Pi does not have. Pi exited at once with `Error: Model "gpt-6.2-terra" not found`, and the runner recorded that as a ticket failure: `TASK-384` and `TASK-474`, both freshly `todo`, went `doing` → `error`, each with a `Runner error (agent)` note on its branch. Nothing was wrong with either ticket, and the loop kept running, so every `todo` ticket it reached would be marked the same way. An agent that fails before committing anything has told us about the runner or its environment, not the ticket.

Decisions:

- A start failure is: the agent sessions run by `_agent_sessions` (`src/chitty/run.py`) raise because a session exited non-zero or its command was not found, and the ticket worktree `HEAD` (`git rev-parse HEAD` in the worktree) is the same commit it was just before `_agent_sessions` was called. No time limit is used. A session that ran for an hour and then crashed without committing is also treated as a start failure: it produced nothing to record against the ticket, and stopping the loop is the right response to an agent that keeps failing.
- Not start failures, unchanged: an agent timeout (`agent timed out after ...`), an interrupt (`RunInterrupted`), the "was unchanged" error after continuations, `RepairError`, and any failure after the agent committed. The review rebase session (`_run_session(..., "rebase")`, called directly near line 940) keeps its current handling; `tests/test_review_rebase_session.py` must pass unchanged.
- New `AgentSessionFailed(ChittyError)` in `src/chitty/run.py`, raised by `_run_session` in place of the plain `ChittyError` for `agent exited with status <N>:\n<output>` and `agent command not found: <command>`, with the same messages. New `AgentStartFailed(ChittyError)`, re-raised past the `except ChittyError` in `_run_ticket` exactly as `RepairError` is, so the CLI prints it and exits 1. `loop_step` already stops `chitty run --loop` on exit 1; no loop change is needed.
- In `_run_ticket`, record the worktree `HEAD` just before `_agent_sessions`, and catch `AgentSessionFailed` around that call. If `HEAD` is unchanged, set the ticket back to `selected_status` on its branch when it differs from the current status (`Repo(worktree, main_repo.config).edit(action.id, Edit(status=selected_status, skip_verdicts=True, skip_current_version=True))`, no note), then raise `AgentStartFailed`. Its message is exactly `agent failed before committing anything; <ID> left at <status>: <detail>`, where `<detail>` is the `AgentSessionFailed` message. If `HEAD` moved, re-raise it, so it is recorded as `Runner error (agent)` as today.
- Agent output goes to stderr through the error message only, never into the ticket.
- The worktree is left as it is: files the agent wrote but did not commit stay, and the next session in that worktree sees them. Nothing is reset or cleaned.
- Repair mode: `selected_status` is `error`, which is already the status, so a repair agent that fails before committing leaves the ticket at `error` with no edit, and the loop stops as for any start failure.
- `HEAD` is compared with the commit recorded before the first session, so a first session that exits 0 without committing, followed by a continuation that exits non-zero, is also a start failure.
- For a `todo` ticket the claim commit (`doing`, made by `claim_edit()` before the agent) stays on the branch, and the reset to `todo` is one more commit: `main..task-1` has exactly two commits afterwards.
- Usage is still recorded by the `finally` block in `_run_ticket`, as for any run.
- `_preflight` only checks that `agent_command` is set, so a command that does not exist reaches `_run_session` and its `FileNotFoundError`.
- Docs: in `docs/plan/next-action-and-runner.md`, add one bullet next to the `agent_timeout` bullet describing the start failure rule and that the loop stops.

Tests. No property: the behaviour needs a real agent process and Git, and the decision has a small fixed set of cases, each listed below. Put the new tests in `tests/test_run_errors_on_branch.py` (`TestRunErrorsOnBranch`), using its fake agent at `self.root / "bin" / "fake"`.

- `test_agent_start_failure_on_todo_stops_and_leaves_todo`: the fake writes `scratch.txt` (without adding or committing it), prints `Error: Model "x" not found` and exits 7; `TASK-1` is `todo`. `run_cli("run", "--ticket", "TASK-1", exit_code=1)`. stderr contains `agent failed before committing anything; TASK-1 left at todo: agent exited with status 7:` and `Error: Model "x" not found`. The ticket on `task-1`'s tip says `status: todo` and contains no `Runner error`; `main` is unchanged; `chitty show TASK-1 --json` reports `todo`; `.worktrees/task-1/scratch.txt` still exists; `git rev-list --count main..task-1` is `2`.
- `test_agent_start_failure_on_doing_leaves_doing`: the same with `make_doing_branch()`. The ticket stays `doing`, the branch tip ticket has no `Runner error`, and no new commit is made on `task-1`.
- `test_repair_start_failure_stops_and_leaves_error`: first run the existing scenario of `test_agent_failure_keeps_error_and_message_on_branch` (`make_doing_branch()`, a fake that commits `work.txt` and exits 7), so `TASK-1` is `error` on `task-1` with a `Runner error (agent)` note. Then replace the fake with one that exits 7 without committing, record `git rev-parse task-1`, and run `run_cli("run", "--errors", "--ticket", "TASK-1", exit_code=1)`. stderr contains `agent failed before committing anything; TASK-1 left at error:`, and `task-1` still points at the recorded commit.
- `test_missing_agent_command_stops_and_leaves_todo`: `agent_command` set to `no-such-chitty-agent {mode} {id}` and committed on `main`; exit 1, stderr contains `agent command not found: no-such-chitty-agent`, the ticket is `todo`.
- `test_agent_failure_keeps_error_and_message_on_branch` (existing): change its fake so it first writes `work.txt`, runs `git add work.txt` and `git commit --quiet -m work`, then exits 7. Its assertions stay unchanged, so a failure after a commit is still recorded as `Runner error (agent)`. Adjust `assert_branch_error` only if the extra commit breaks its `task-1~1` parent check, and say how in the notes.

## Acceptance Criteria

- [ ] The four new tests pass; a note records that each fails against `src/chitty/run.py` of `main` before this change on a status, stderr or commit-count assertion (today the ticket goes to `error` and the run exits 0)
- [ ] The changed `test_agent_failure_keeps_error_and_message_on_branch` and every test in `tests/test_review_rebase_session.py` and `tests/test_run_timeout.py` pass; a note records that the changed test fails against a version that treats every non-zero agent exit as a start failure, ignoring `HEAD`
- [ ] `docs/plan/next-action-and-runner.md` has the start-failure bullet next to the `agent_timeout` bullet; `make check` passes

## Plan

Add specified real-process regression cases and verify they fail before the fix; distinguish session failures and compare worktree HEAD before recording errors, preserving status and files on start failure. Verify the post-commit case against an intentionally broken comparison, update the runner plan, and run the required checks.

## Notes

Suggestion origin: chitty

Cold read 2026-11-21 outcomes: repair start failures leave the ticket at `error` and stop the loop, with a test; the worktree is left as it is after a start failure, and the todo test checks an uncommitted file survives.

Second cold read 2026-11-21 outcomes: the claim commit stays and the branch count is pinned; the repair fixture is built from the existing agent-failure scenario; an empty first session followed by a failing continuation is a start failure; usage is still recorded; `_preflight` does not check that the command exists (verified). Today the run exits 0 (`run_cli` defaults to `exit_code=0` in the existing test). Not adopted: a test for the continuation case, which uses the same `HEAD` comparison as the tested cases.

## History

- 2026-11-21T07:57:47Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:48Z nimble-umber-gannet: changed notes
- 2026-11-21T08:00:33Z nimble-umber-gannet: changed title, labels, priority, description, acceptance criteria
- 2026-11-21T08:00:33Z nimble-umber-gannet backlog → cold-read
- 2026-11-21T08:01:52Z nimble-umber-gannet: changed description, acceptance criteria, notes
- 2026-11-21T08:01:52Z nimble-umber-gannet cold-read → planning
- 2026-11-21T08:02:12Z nimble-umber-gannet planning → cold-read
- 2026-11-21T08:03:48Z nimble-umber-gannet: changed description, notes
- 2026-11-21T08:03:48Z nimble-umber-gannet cold-read → todo
- 2026-11-21T08:49:33Z jolly-hazel-kestrel todo → doing
- 2026-11-21T08:52:23Z jolly-hazel-kestrel: wrote the plan
