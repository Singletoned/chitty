---
title: Report `chitty run` errors to a configured command
status: review
created: 2026-11-11
---

## Description

- Errors from `chitty run --loop` show only in its terminal, and are easy to miss.
- Add an optional root setting `error_reporter`, a command parsed like `agent_command` (split first, then each word substituted in one pass, so a message containing spaces, quotes or `{context}` stays one argument). When `chitty run` fails with a Chitty error, it runs this command with `{message}` (the error text) and `{context}` (JSON with `actor`, and `project`, `ticket` and `mode` once known), then exits as before. Hook it in `run()` in `src/chitty/run.py`, where the config and ticket are known.
- Not reported: an empty queue (`NoNextTicket`), Ctrl-C (`RunInterrupted`), and config errors before the config loads. Under `--loop`, each failing child reports once and the parent does not.
- A failing reporter prints a warning and does not hide the original error.
- After this lands, the planner sets `error_reporter = "sump capture chitty --message {message} --context-json {context}"` on `main`; the branch leaves `chitty.toml` alone. TASK-256 later reads errors back from Sump.
- Document it in `README.md` and `PLAN.md` "Config".

## Acceptance Criteria

- [x] With `error_reporter` set to a script that writes its arguments to a file, a `chitty run` whose agent command exits 1 leaves the message and a JSON context naming the ticket in that file, and still exits non-zero. It fails today.
- [x] Without `error_reporter`, behaviour is unchanged; with it, a successful run and an empty queue run no reporter.
- [x] A reporter that exits non-zero prints a warning, and `chitty run` still fails with the agent's error.
- [x] With `error_reporter` set, `chitty run --ticket TASK-1 --mode work` runs the reporter with the message `--mode cannot be used with --ticket`, and still exits non-zero. Every other Chitty error `run()` raises after the config loads is reported the same way. It fails today.

## Plan

Move the error-reporting try boundary in src/chitty/run.py so it includes post-configuration argument validation; preserve reporter context and exclusions. Add a regression integration test for --ticket with --mode, verify it fails before the fix, then passes. Run chitty fix, make format/check, and commit implementation.

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

## Summary

Implemented configured error reporting for Chitty run failures, including post-config argument validation, preserved exclusions/context, and documented the setting. Regression tests confirmed the reported validation error failed before the fix and passes now. Merged main, resolved the PLAN.md Config conflict, and verified with make format && make check (517 Python test suites and Node tests). No follow-ups.

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
