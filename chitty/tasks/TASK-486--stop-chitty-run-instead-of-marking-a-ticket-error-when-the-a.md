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
- A command missing from `PATH` is already refused by `_agent_command` (`agent_command executable is not on PATH: ...`) before the worktree is made, exits 1 and leaves the ticket unchanged (`tests/test_next.py`, near line 1995). That stays as it is, with no new test. `_run_session`'s `FileNotFoundError` branch (`agent command not found`) still raises `AgentSessionFailed`, for a command removed between that check and the session.
- Docs: in `docs/plan/next-action-and-runner.md`, add one bullet next to the `agent_timeout` bullet describing the start failure rule and that the loop stops.

Tests. No property: the behaviour needs a real agent process and Git, and the decision has a small fixed set of cases, each listed below. Put the new tests in `tests/test_run_errors_on_branch.py` (`TestRunErrorsOnBranch`), using its fake agent at `self.root / "bin" / "fake"`.

- `test_agent_start_failure_on_todo_stops_and_leaves_todo`: the fake writes `scratch.txt` (without adding or committing it), prints `Error: Model "x" not found` and exits 7; `TASK-1` is `todo`. `run_cli("run", "--ticket", "TASK-1", exit_code=1)`. stderr contains `agent failed before committing anything; TASK-1 left at todo: agent exited with status 7:` and `Error: Model "x" not found`. The ticket on `task-1`'s tip says `status: todo` and contains no `Runner error`; `main` is unchanged; `chitty show TASK-1 --json` reports `todo`; `.worktrees/task-1/scratch.txt` still exists; `git rev-list --count main..task-1` is `2`.
- `test_agent_start_failure_on_doing_leaves_doing`: the same with `make_doing_branch()`. The ticket stays `doing`, the branch tip ticket has no `Runner error`, and no new commit is made on `task-1`.
- `test_repair_start_failure_stops_and_leaves_error`: first run the existing scenario of `test_agent_failure_keeps_error_and_message_on_branch` (`make_doing_branch()`, a fake that commits `work.txt` and exits 7), so `TASK-1` is `error` on `task-1` with a `Runner error (agent)` note. Then replace the fake with one that exits 7 without committing, record `git rev-parse task-1`, and run `run_cli("run", "--errors", exit_code=1)` (the CLI rejects `--errors` with `--ticket`; `TASK-1` is the only `error` ticket, so `--errors` selects it). stderr contains `agent failed before committing anything; TASK-1 left at error:`, and `task-1` still points at the recorded commit.
- `test_agent_failure_keeps_error_and_message_on_branch` (existing): change its fake so it first writes `work.txt`, runs `git add work.txt` and `git commit --quiet -m work`, then exits 7. Its assertions stay unchanged, so a failure after a commit is still recorded as `Runner error (agent)`. Adjust `assert_branch_error` only if the extra commit breaks its `task-1~1` parent check, and say how in the notes.

Existing tests (decided 2026-11-21, after the first implementation found six failing):

- A start failure is a runner or environment problem, so `error_reporter` runs for it, as it does for interrupts and argument errors: `AgentStartFailed` reaches the CLI's error path like any other `ChittyError`. Add `test_agent_start_failure_calls_reporter` to `tests/test_run_error_reporter.py`: a reporter configured as in its other tests, a fake agent that exits 7 without committing; the run exits 1 and the reporter is called once with a message containing `agent failed before committing anything`.
- The six tests that fail today keep their purpose, which is a failure after the agent has done work: `tests.test_next.TestNext.test_run_cases`, `tests.test_next.TestNext.test_run_write_failure_warns_and_keeps_agent_exit_code`, `tests.test_review_merge.TestReviewMerge.test_missing_review_branch_errors_and_is_selected_for_repair`, the two failure cases in `tests/test_run_error_reporter.py` (including `test_recoverable_ticket_failure_does_not_call_reporter`), and `tests.test_run_lock.TestRunLock.test_a_run_holds_the_lock_and_frees_it_however_it_ends`. In each, make the failing fake agent commit before it exits non-zero (`git commit --allow-empty --quiet -m agent` is enough: it moves `HEAD`), and keep the test's assertions. Where the fake agent is shared, an opt-in environment variable on it is fine. A repair agent that failed with `nothing to commit` uses `--allow-empty` too. List each changed fixture in a note.

## Acceptance Criteria

- [ ] The three new tests pass; a note records that each fails against `src/chitty/run.py` of `main` before this change on a status, stderr or commit-count assertion (today the ticket goes to `error` and the run exits 0)
- [ ] The changed `test_agent_failure_keeps_error_and_message_on_branch` and every test in `tests/test_review_rebase_session.py` and `tests/test_run_timeout.py` pass; a note records that the changed test fails against a version that treats every non-zero agent exit as a start failure, ignoring `HEAD`
- [ ] `docs/plan/next-action-and-runner.md` has the start-failure bullet next to the `agent_timeout` bullet; `make check` passes
- [ ] `test_agent_start_failure_calls_reporter` passes and fails against `main`'s `src/chitty/run.py`; the six existing tests named in the Description pass with only their fake agents changed

## Plan

Update the specified existing agent fixtures and add the reporter regression, verify it fails against main, then run formatting and full checks.

## Notes

Suggestion origin: chitty

Cold read 2026-11-21 outcomes: repair start failures leave the ticket at `error` and stop the loop, with a test; the worktree is left as it is after a start failure, and the todo test checks an uncommitted file survives.

Second cold read 2026-11-21 outcomes: the claim commit stays and the branch count is pinned; the repair fixture is built from the existing agent-failure scenario; an empty first session followed by a failing continuation is a start failure; usage is still recorded; `_preflight` does not check that the command exists (verified). Today the run exits 0 (`run_cli` defaults to `exit_code=0` in the existing test). Not adopted: a test for the continuation case, which uses the same `HEAD` comparison as the tested cases.

Implementation stopped: two requirements contradict current code. `src/chitty/cli.py` rejects `--errors` combined with `--ticket`, so the prescribed repair test exits 2 before reaching the agent. Decide whether to allow that combination or change the test invocation. Also, although `_preflight` only checks that the command is set, `_agent_command` checks `shutil.which` before creating the worktree and raises `agent_command executable is not on PATH: ...`; a nonexistent command cannot reach `_run_session` as claimed. Decide whether to remove or change that validation and how to preserve its existing behavior and tests. Both decisions affect scope and the prescribed regression assertions, so the ticket cannot guide implementation as written. Experimental tests were removed; no implementation changes remain. Before discovering these issues, the todo and doing start-failure tests failed against the existing runner because it exited 0 and recorded an error; the repair and missing-command tests instead exposed the contradictions above. Required implementation verification remains unfinished.

Return to planning: the prescribed repair invocation is rejected by the CLI, and missing agent commands are rejected by `_agent_command` before `_run_session`. See the preceding note for the required decisions and verification evidence.

Replanned 2026-11-21: both blockers in the notes above are settled in the Description. The repair test runs plain `--errors`; the missing-command test is dropped because `_agent_command` already refuses a command not on `PATH`.

Reviewed the runner and refreshed the implementation plan; no code or tests have been changed, and required regression and verification work remains.

All three new regression tests failed against the original runner: each expected exit 1 but received exit 0. The post-commit fixture leaves the parent ticket unchanged, so assert_branch_error needed no adjustment.

The changed post-commit test fails when the HEAD comparison is deliberately disabled: expected exit 0, got 1. Restored the comparison afterward.

Implementation and specified focused tests pass (36 tests). make check fails six existing tests: tests.test_next.TestNext.test_run_cases and test_run_write_failure_warns_and_keeps_agent_exit_code, tests.test_review_merge.TestReviewMerge.test_missing_review_branch_errors_and_is_selected_for_repair, both tests.test_run_error_reporter failure cases, and tests.test_run_lock.TestRunLock.test_a_run_holds_the_lock_and_frees_it_however_it_ends. These fixtures assume an uncommitted failing agent is a recoverable ticket error. In particular the error-reporter test expects no reporter call, but the new propagated CLI error invokes it; the ticket does not specify whether start failures should invoke the reporter. Decide reporter behavior and specify the necessary updated existing-test fixtures and assertions, including the repair agent that currently fails because its git commit has nothing to commit. Until then make check cannot pass and full verification is unfinished. Implementation is preserved in the branch.

Return to planning: the required full check exposes six existing tests that assume the old failure behavior, including an unspecified error-reporter decision. See the preceding note for evidence and decisions needed.

Replanned 2026-11-21 (overnight planner): reporter and existing-test decisions are in the Description, under "Existing tests". Implementation on the branch is kept.

Check failed before this session: check exited with status 2; output in `.chitty/check.log`

Added reporter start-failure regression; it passes on the branch. Attempting it with current main run.py failed before the assertion because main expects RepoConfig.command_timeout, absent on this branch; a compatible main baseline is still needed. make check remains failing on the existing fixtures; updating those and verifying reporter invocation count remain unfinished.

Reporter regression fails against the pre-implementation runner from afedf3c2 parent (exit 0 instead of 1) and passes on this branch, including exactly one reporter invocation. Updated failing fake agents in test_run_cases, test_run_write_failure_warns_and_keeps_agent_exit_code, the shared review repair agent, both reporter failure cases, and the lock test to commit before failure; the repair fake exits nonzero after its empty commit. make check passes all 905 tests.

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
- 2026-11-21T08:53:27Z jolly-hazel-kestrel: changed notes
- 2026-11-21T08:53:40Z jolly-hazel-kestrel: changed owner, notes
- 2026-11-21T08:53:40Z jolly-hazel-kestrel doing → planning
- 2026-11-21T22:55:00Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-21T22:55:10Z lively-zinc-newt planning → cold-read
- 2026-11-21T22:55:49Z lively-zinc-newt: changed notes
- 2026-11-21T22:55:49Z lively-zinc-newt cold-read → todo
- 2026-11-21T22:56:08Z honest-dusky-stoat todo → doing
- 2026-11-21T22:57:46Z honest-dusky-stoat: wrote the plan
- 2026-11-21T22:57:59Z honest-dusky-stoat: changed notes
- 2026-11-21T22:58:45Z honest-dusky-stoat: changed notes
- 2026-11-21T23:00:39Z honest-dusky-stoat: changed notes
- 2026-11-21T23:02:42Z honest-dusky-stoat: changed notes
- 2026-11-21T23:02:54Z honest-dusky-stoat: changed owner, notes
- 2026-11-21T23:02:54Z honest-dusky-stoat doing → planning
- 2026-11-21T23:14:11Z lively-zinc-newt: changed description, acceptance criteria, notes
- 2026-11-21T23:14:11Z lively-zinc-newt planning → todo
- 2026-11-21T23:17:46Z vivid-pearl-urchin todo → doing
- 2026-11-21T23:19:04Z vivid-pearl-urchin: changed notes
- 2026-11-21T23:19:18Z vivid-pearl-urchin: wrote the plan
- 2026-11-21T23:21:19Z vivid-pearl-urchin: changed notes
- 2026-11-21T23:25:19Z vivid-pearl-urchin: changed notes
