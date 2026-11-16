---
title: Hide role guides under the tickets workflow
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-330
  - TASK-332
  - TASK-333
  - TASK-335
created: 2026-11-14
---

## Description

Under `workflow = "tickets"` (the resolved `config.workflow` from TASK-330), hide the role guides.

- `chitty guide` with no role still prints the managed block (TASK-332 decides its text).
- Every role in `ROLE_NAMES` (`work`, `review`, `repair`, `plan`, `cold-read`, `setup`) is unavailable: `chitty guide <role> [ID]` exits 1 with `chitty guide <role> needs workflow = "runner" in the Chitty config`, and `chitty guide --help` shows only the plain `chitty guide` example, with no role examples or the line about which roles take an ID.
- Put the refusal in `guide(role, workflow, ticket_id)` in `src/chitty/store.py`. `workflow` is a required parameter with no default, so every caller decides; update the existing callers and tests (about 20 test files pass `"runner"`). `src/chitty/run.py` passes `repo.config.workflow`; under `tickets` TASK-333 already refuses `run` before it reaches this.
- When no config is found, behave as `runner`, as today. When the config fails to load, `chitty guide` and `chitty guide <role>` report the config error and exit 1, like other commands; only `chitty guide --help` falls back to the runner help, so help still works while diagnosing a broken config (the same rule as TASK-333).
- TASK-335 adds `workflow = "runner"` to `tests/support.py`; do not add it again.
- No property test: a small fixed set (six roles, two workflows, no repository), each case tested. Tests go in `tests/test_guide_workflow.py`.

## Acceptance Criteria

- [x] In a temp repository with `workflow = "tickets"`, for each of the six roles, `chitty guide <role>` exits 1, prints nothing on stdout, and prints the message naming the role and `workflow = "runner"` on stderr. Fails today.
- [x] Under `tickets`, `chitty guide` exits 0 and prints the managed block, and `chitty guide --help` mentions no role name.
- [ ] Under `runner`, and outside a repository, `chitty guide`, each role with and without `TASK-1`, and `chitty guide --help` give the same stdout, stderr and exit code as at the commit before this change (capture them there first). With a config that fails to load, `chitty guide work` exits 1 with the config error and `chitty guide --help` shows the runner help. `make check` passes.

## Plan

Add explicit compatibility assertions in tests/test_guide_workflow.py for runner and outside-repository invocation cases, covering stdout, stderr, and exit status for general guide, all roles with and without TASK-1, and help. Capture expected results from the pre-change revision inside this worktree, accounting for main changes merged afterward; then run the focused tests, format/check, and commit the test-only follow-up.

## Notes

Cold read starting point: `refs/cold-read/TASK-334/1` (on top of TASK-332's read; mutants M1 to M4 killed). Its main files: `src/chitty/store.py`, `src/chitty/cli.py` (`_GuideCommand`), `src/chitty/run.py`, `tests/test_guide_workflow.py`; see them with `git show refs/cold-read/TASK-334/1:<path>`. It differs from the current text: its `role_workflow` falls back to runner on a broken config for role guides, which the ticket now forbids, and it also edits `tests/support.py`, which TASK-335 owns. Check it against the current criteria rather than trusting it.

Regression evidence: tests.test_guide_workflow failed before the fix on all six tickets-workflow role refusals and role-bearing help; after the implementation, the workflow and compatibility tests pass. Verification: make format && make check passed (591 Python test suites and Node tests); git status --short was empty after commit c7ed80f.

Review failed (tests): Newly discovered coverage gap: add the required baseline-capture compatibility tests for every specified case to tests/test_guide_workflow.py, checking stdout, stderr and exit code rather than comparing current output with the current implementation. No earlier review findings exist.
1: pass - tests.test_guide_workflow passes; running TestRoleGuidesUnderTickets against c7ed80f^ printed FAILED (failures=7), including all six refusals. A separate six-role probe with TASK-1 printed six roles refused.
2: pass - TestRoleGuidesUnderTickets passes; against c7ed80f^ it failed because help contained work. The managed guide assertion passed in both versions.
3: fail - tests/test_guide_workflow.py does not capture baseline output or exercise all runner and outside-repository cases and all three result fields: it omits general guide, plan/setup with ID, most outside cases, exit codes and stderr. The required fixed-case compatibility tests are missing. Independent comparison against current main printed runner 14 comparisons; differences: [] and outside 14 comparisons; differences: [] (outside simulated by patching root discovery). Broken TOML probes printed exit 1 for guide and guide work, and help exit 0 with the runner example. make format && make check passed: 588 Python tests and Node tests. Comparing to c7ed80f^ instead showed setup output differences from a separately merged main change, so baseline selection must account for that merge.

Review follow-up cannot be completed safely from the current criterion: “same output as at the commit before this change” does not identify whether the baseline is the pre-implementation parent c7ed80f^ (which includes an upstream merge and has unrelated setup-guide output differences) or the earlier implementation base before that merge. The review explicitly observed different setup output when comparing against c7ed80f^ and says baseline selection must account for the merge. Please decide which behavior is the compatibility contract (the exact pre-change tree, or behavior with unrelated merged-main changes excluded) and identify the baseline revision. Until then, snapshots risk locking in unrelated changes or testing the wrong output.

## Summary

Implemented workflow-gated role guides. CLI loads repository config for role requests (broken config errors propagate), defaults to runner outside repositories, runner help remains available when config is broken, and run.py passes repo.config.workflow. Added six-role workflow tests and updated direct callers. Verified with make format and make check; regression tests were observed failing before the fix. Commit: c7ed80f. No known follow-ups.

## History

- 2026-11-14T18:21:59Z friendly-ginger-adder → planning
- 2026-11-14T18:23:32Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:29:50Z friendly-ginger-adder: changed description, acceptance criteria
- 2026-11-14T18:30:01Z friendly-ginger-adder: changed dependencies
- 2026-11-14T18:56:14Z friendly-ginger-adder: changed owner
- 2026-11-14T18:56:14Z friendly-ginger-adder planning → cold-read
- 2026-11-14T19:25:40Z friendly-ginger-adder: changed dependencies, description, acceptance criteria, notes
- 2026-11-14T19:25:40Z friendly-ginger-adder cold-read → planning
- 2026-11-14T19:25:41Z friendly-ginger-adder: changed owner
- 2026-11-14T19:25:41Z friendly-ginger-adder planning → todo
- 2026-11-16T10:56:50Z jolly-khaki-yellowhammer todo → doing
- 2026-11-16T10:57:15Z jolly-khaki-yellowhammer: wrote the plan
- 2026-11-16T11:01:00Z jolly-khaki-yellowhammer: changed notes, summary; ticked acceptance criteria
- 2026-11-16T11:01:00Z jolly-khaki-yellowhammer doing → review
- 2026-11-16T11:04:20Z vivid-navy-newt: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-16T11:04:20Z vivid-navy-newt review → doing
- 2026-11-16T11:13:52Z honest-hazel-yellowhammer: wrote the plan
- 2026-11-16T11:14:42Z honest-hazel-yellowhammer: changed owner, notes
- 2026-11-16T11:14:42Z honest-hazel-yellowhammer doing → planning
