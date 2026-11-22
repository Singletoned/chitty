---
title: Hide role guides under the tickets workflow
status: cold-read
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

Under `workflow = "tickets"` (the resolved `RepoConfig.workflow`), hide the role guides. Replanned 2026-11-22 against `main`: `ROLE_NAMES` in `src/chitty/store.py` now has seven roles (`work`, `review`, `repair`, `plan`, `cold-read`, `setup`, `rebase`) and `guide` takes a keyword-only `directory`.

Decisions:

- `chitty guide` with no role is unchanged (`repository_guide`).
- Add a keyword-only parameter `workflow: str` with no default to `guide(role, ticket_id=None, *, directory)` in `src/chitty/store.py`. When `workflow != "runner"`, it raises `ChittyError(f'chitty guide {role} needs workflow = "runner" in the Chitty config')` after the unknown-role check and before anything else. Update every caller: the three in `src/chitty/run.py` (around line 978) pass `repo.config.workflow`; tests that call `guide(` pass `workflow="runner"`.
- `guide_` in `src/chitty/cli.py` passes `configured_workflow(Path.cwd())`, or `"runner"` when that returns `None` (outside a repository). A config that fails to load raises from `configured_workflow`, so `chitty guide` with a role exits 1 with the config error. `chitty guide` with no role already does the same through `repository_guide`.
- `chitty guide --help` under `tickets` shows only the plain `chitty guide` example line: no role example lines and no line about which roles take an ID. Do this with a `click.Command` subclass for `guide_` that uses the existing `_tickets_workflow()` in `cli.py`, which already treats a broken or missing config as runner, so help still works while diagnosing a broken config (the rule `RUNNER_COMMANDS` follows).
- The old branch `task-334` (commit `c7ed80f`) predates the seventh role and the `directory` parameter. Use it as a reference, but the result must match current `main`.

Tests in `tests/test_guide_workflow.py` (it exists on the branch; create it if the rebase drops it), with `CliRunner` in temporary repositories as `RepoTestCase` sets up. No property: a fixed set of seven roles, two workflows and outside a repository, each case tested. The runner cases do not compare against a captured baseline: a snapshot of guide text would break whenever a guide changes, and the branch's merge with `main` made the baseline ambiguous (2026-11-21 review).

## Acceptance Criteria

- [ ] In a temporary repository with `workflow = "tickets"`, for each role in `ROLE_NAMES`, `chitty guide <role>` and (for roles other than `plan` and `setup`) `chitty guide <role> TASK-1` exit 1, print nothing on stdout, and print `chitty guide <role> needs workflow = "runner" in the Chitty config` on stderr; this fails before the change
- [ ] Under `tickets`, `chitty guide` exits 0 and prints `managed_guide("tickets")`, and `chitty guide --help` exits 0, contains `chitty guide` and contains no role name from `ROLE_NAMES`; this fails before the change
- [ ] With `workflow = "runner"`, and in a directory outside any repository, each role with and without `TASK-1` (where accepted) exits 0 with empty stderr and stdout containing the first line of `src/chitty/roles/<role>.md`, and `chitty guide --help` contains every example line of the current help; with an invalid `workflow` value, `chitty guide work` exits 1 naming `workflow` and `chitty guide --help` still shows the runner examples; `make check` passes

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
- 2026-11-22T09:47:18Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T09:47:18Z friendly-jade-stoat planning → cold-read
