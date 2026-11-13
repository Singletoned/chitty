---
title: Report `chitty run` errors to a configured command
status: done
created: 2026-11-11
---

## Description

- Errors from `chitty run --loop` show only in its terminal, and are easy to miss.
- Add an optional root setting `error_reporter`, a command parsed like `agent_command` (split first, then each word substituted in one pass, so a message containing spaces, quotes or `{context}` stays one argument). When `chitty run` fails with a Chitty error, it runs this command with `{message}` (the error text) and `{context}` (JSON with `actor`, and `project`, `ticket` and `mode` once known), then exits as before. Hook it in `run()` in `src/chitty/run.py`, where the config and ticket are known.
- Not reported: an empty queue (`NoNextTicket`), Ctrl-C (`RunInterrupted`), and config errors before the config loads. Under `--loop`, each failing child reports once and the parent does not.
- A failing reporter prints a warning and does not hide the original error.
- After this lands, the planner sets `error_reporter = "sump capture chitty --message {message} --context-json {context}"` on `main`; the branch leaves `chitty.toml` alone. TASK-256 later reads errors back from Sump.
- Document it in `README.md` and `docs/plan/config.md`.

## Acceptance Criteria

- [x] With `error_reporter` set to a script that writes its arguments to a file, a `chitty run` whose agent command exits 1 leaves the message and a JSON context naming the ticket in that file, and still exits non-zero. It fails today.
- [x] Without `error_reporter`, behaviour is unchanged; with it, a successful run and an empty queue run no reporter.
- [x] A reporter that exits non-zero prints a warning, and `chitty run` still fails with the agent's error.
- [x] With `error_reporter` set, `chitty run --ticket TASK-1 --mode work` runs the reporter with the message `--mode cannot be used with --ticket`, and still exits non-zero. Every other Chitty error `run()` raises after the config loads is reported the same way. It fails today.

## Plan

Move Git main-checkout discovery and Repo.open inside the error-reporting boundary, using the input repo to report failures before main_repo exists. Add a regression integration test that removes the temporary repository Git metadata and confirms the configured reporter receives the failure. Run the regression before the fix, then chitty fix, make format/check, commit, and update ticket verification.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-289/1`. Check it against the current criteria; do not trust it.

Regression tests failed before implementation (unknown error_reporter config; no report file), then passed after implementation. `make format && make check` passes all 502 Python suites and Node tests. Empty queue is an expected exit status 3 and does not invoke reporter. Commit: 14688ec.

Review failed (tests): Cover and report Chitty errors raised by argument validation after configuration loads. A throwaway integration run with a configured file-writing reporter and `run --ticket TASK-1 --mode work` printed `Error: --mode cannot be used with --ticket` and `report exists: False`; it must invoke the reporter. Validation occurs before the reporting handler. The CLI refused the transition to doing because all criterion verdicts pass, although the description requirement fails.
1: pass - `make format && make check` passed; `test_failing_run_reports_message_and_ticket_context` passed, and disabling `report_error` made it error with a missing report file.
2: pass - `make check` passed existing runs without a reporter and the empty queue test; a throwaway successful `TestRunContinue` integration run with a configured reporter printed `successful run: 0 report exists: False`.
3: pass - A throwaway failing-reporter integration run printed `warning: error_reporter exited with status 7` and `Error: agent exited with status 1`, exit 1; disabling `report_error` made `test_failing_reporter_warns_and_preserves_failure` fail.

Review blocked: The configured reporter is not invoked for the post-configuration Chitty error from `run --ticket TASK-1 --mode work`, contrary to the description. All numbered criteria passed, so Chitty rejected the requested transition to doing with `moving review → doing requires at least one fail verdict`. A human must resolve the mismatch between the review workflow and this demonstrated defect. See the preceding review note for evidence and criterion verdicts.

Planner, 2026-11-12: added criterion 4 for the defect the last review found (argument errors in `run()` are raised before the reporting `try`, so they are not reported). Move the `try` to cover them; the earlier criteria still stand.

Regression test test_argument_error_reports_message_and_ticket_context failed before the fix because the reporter file was not created, then passed afterward. Validation remains before Git preflight and reports using the already-loaded repo config. make format && make check passed (505 Python tests and Node tests); committed as 8dced16.

Review failed (integration): merging `main` conflicts in `PLAN.md`.

Merged main; resolved the PLAN.md Config conflict by retaining both error_reporter and job_order settings. make format && make check passes on the merged branch (517 Python test suites and Node tests). chitty fix passes with pre-existing task-content warnings.

Review failed (tests): Cover errors from main checkout discovery after configuration loads and move that operation inside the reporter boundary. A configured reporter is not invoked when Git discovery fails.
1: pass - `make format && make check` printed `Ran 518 tests` and `OK`; disabling `report_error` made `test_failing_run_reports_message_and_ticket_context` error with a missing report file.
2: pass - `make check` passed existing runs and `test_empty_queue_does_not_report`; the preceding review also ran a successful configured-reporter run and printed `successful run: 0 report exists: False`.
3: pass - `make check` passed `test_failing_reporter_warns_and_preserves_failure`; disabling `report_error` made that test fail. The preceding review ran the failing reporter and printed `warning: error_reporter exited with status 7` and `Error: agent exited with status 1`.
4: fail - `test_argument_error_reports_message_and_ticket_context` passes and errors with a missing report when reporting is disabled, but a throwaway CLI run with configured reporter after removing the temporary repository `.git` printed `Error: `git rev-parse --git-common-dir` failed` and `report exists: False`. This post-config Chitty error must also be reported.

Third failed review: blocked for human resolution. See the preceding review note for the unmet criterion and reproduction.

Planner, 2026-11-12: `main` split `PLAN.md` into `docs/plan/` (commit `23ba131`). Merging `main` gives a modify/delete conflict on `PLAN.md`: move this branch's `error_reporter` lines into `docs/plan/config.md` and delete `PLAN.md`.

Planner, 2026-11-12: the third review is right. `git.main_checkout()` and `Repo.open()` in `run()` raise before the reporting `try`, so their errors (for example a repository whose `.git` is gone) are not reported. Start the `try` straight after `repo` is passed in, before `git.main_checkout`, and add a regression test for that case. Merging `main` will also conflict on `PLAN.md`: see the note above.

Added test_main_checkout_discovery_error_reports. It failed before the fix because reporter output was absent, then passed after moving Git discovery and Repo.open inside the reporter boundary; it verifies the Chitty error is recorded. make format && make check passed (519 Python tests and Node tests). chitty fix passed with existing task-content warnings. Implementation committed as 31d8c94; worktree clean.

Review failed (integration): merging `main` conflicts in `PLAN.md`.

Merged main; resolved PLAN.md deletion by carrying error_reporter documentation into docs/plan/config.md. make format && make check passed (519 Python tests and Node tests). chitty fix on the TASK-289 task file passed. Worktree clean.

Reviewed: `make format && make check` passed: 519 Python tests and Node tests; worktree remained clean.
1: pass - `test_failing_run_reports_message_and_ticket_context` passed; with `report_error` disabled in memory it errored with missing report.json.
2: pass - `test_empty_queue_does_not_report` and existing unconfigured runs passed; a configured successful TestRunContinue run printed `successful run: 0 report exists: False`.
3: pass - `test_failing_reporter_warns_and_preserves_failure` passed; disabling `report_error` made it fail on the missing report. Earlier review observed the warning and original agent error.
4: pass - `test_argument_error_reports_message_and_ticket_context` and `test_main_checkout_discovery_error_reports` passed; disabling `report_error` made both error with missing report.json.

## Summary

Error reporting covers configured failures including argument validation and main-checkout discovery, and docs now live in docs/plan/config.md after merging main. Regression test for missing Git metadata fails without the fix and passes with it. Verified with make format && make check (519 Python tests and Node tests) and chitty fix. Main merge committed as 8ff0ce4; implementation commit 31d8c94.

## History

- 2026-11-11T16:17:52Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:21Z vivid-yellowhammer: changed description
- 2026-11-11T18:50:28Z vivid-yellowhammer: changed description
- 2026-11-11T18:50:29Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T18:50:57Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T18:54:56Z vivid-yellowhammer: changed description
- 2026-11-11T18:54:58Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T18:54:58Z vivid-yellowhammer cold-read → todo
- 2026-11-11T21:49:16Z rosy-fawn-badger todo → doing
- 2026-11-11T21:49:37Z rosy-fawn-badger: wrote the plan
- 2026-11-11T21:52:43Z rosy-fawn-badger: changed notes, summary; ticked acceptance criteria
- 2026-11-11T21:52:43Z rosy-fawn-badger doing → review
- 2026-11-11T21:56:50Z rosy-lilac-marten: changed notes
- 2026-11-11T21:57:09Z rosy-lilac-marten: changed owner, notes
- 2026-11-11T21:57:09Z rosy-lilac-marten review → blocked
- 2026-11-12T18:13:28Z kind-yellow-vole: changed owner, acceptance criteria, notes
- 2026-11-12T18:13:28Z kind-yellow-vole blocked → doing
- 2026-11-12T18:18:06Z jolly-yellow-raven: wrote the plan
- 2026-11-12T18:22:53Z jolly-yellow-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-12T18:22:53Z jolly-yellow-raven doing → review
- 2026-11-12T20:23:31Z zesty-umber-puffin: changed notes
- 2026-11-12T20:23:31Z zesty-umber-puffin review → doing
- 2026-11-12T20:27:54Z jolly-silver-zander: changed notes, summary
- 2026-11-12T20:27:54Z jolly-silver-zander doing → review
- 2026-11-12T20:32:03Z lively-khaki-gannet: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-12T20:32:03Z lively-khaki-gannet review → doing
- 2026-11-12T20:32:17Z lively-khaki-gannet: changed owner, notes
- 2026-11-12T20:32:17Z lively-khaki-gannet doing → blocked
- 2026-11-12T21:35:10Z kind-yellow-vole: changed description, notes
- 2026-11-12T21:43:22Z kind-yellow-vole: changed owner, notes
- 2026-11-12T21:43:22Z kind-yellow-vole blocked → doing
- 2026-11-12T21:44:35Z calm-coral-raven: wrote the plan
- 2026-11-12T21:47:40Z calm-coral-raven: changed notes, summary; ticked acceptance criteria
- 2026-11-12T21:47:40Z calm-coral-raven doing → review
- 2026-11-13T08:49:03Z zesty-ginger-zander: changed notes
- 2026-11-13T08:49:03Z zesty-ginger-zander review → doing
- 2026-11-13T08:53:35Z kind-ginger-heron: changed notes, summary; ticked acceptance criteria
- 2026-11-13T08:53:35Z kind-ginger-heron doing → review
- 2026-11-13T08:57:31Z sunny-ebony-vole: changed notes; ticked acceptance criteria
- 2026-11-13T08:57:31Z sunny-ebony-vole review → done
