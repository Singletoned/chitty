---
title: Hide role guides under the tickets workflow
status: blocked
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
- Add a keyword-only parameter `workflow: str` with no default to `guide(role, ticket_id=None, *, directory)` in `src/chitty/store.py`. When `workflow != "runner"`, it raises `ChittyError` right after the unknown-role check, before the "does not take a ticket ID" check, so `chitty guide plan TASK-1` under `tickets` gets the workflow message. The message is `chitty guide <role> needs workflow = "runner" in the Chitty config`: move the text `require_runner` in `src/chitty/config.py` builds into a helper `runner_required_message(command: str) -> str` there, used by both `require_runner` and `guide` (with `command = f"guide {role}"`).
- Update every caller of `guide(`: the three in `src/chitty/run.py` (around line 978) pass `repo.config.workflow`; the tests that call it (about 60 call sites) pass `workflow="runner"`.
- `guide_` in `src/chitty/cli.py` passes `configured_workflow(Path.cwd())`, or `"runner"` when that returns `None` (outside a repository). A config that fails to load raises from `configured_workflow`, so `chitty guide <role>` exits 1 with the config error (for an invalid value: `...chitty.toml: workflow: must be a string: 'tickets' or 'runner'`).
- Help: give `guide_` a `click.Command` subclass (`cls=`) that overrides `format_help_text(ctx, formatter)`. When the existing `_tickets_workflow()` in `cli.py` is true it writes a module constant `TICKETS_GUIDE_HELP`: the first docstring line, a blank line, and a `\b` block with only the `chitty guide  General agent instructions` example line; otherwise it calls the parent (today's docstring, unchanged). So under `tickets` neither the role example lines nor the line `Work, review, cold-read and rebase accept an optional ticket ID...` appear. `_tickets_workflow()` treats a missing or broken config as runner, so help still works while diagnosing a broken config, the rule `RUNNER_COMMANDS` follows.
- Out of scope: `README.md`, `AGENTS.md` and `docs/plan/agent-instructions.md`, which list the role guides without the workflow condition; a separate `untestable` ticket that depends on this one updates them.
- The old branch `task-334` (commit `c7ed80f`) predates the seventh role and the `directory` parameter. Use it as a reference, but the result must match current `main`.

Tests in `tests/test_guide_workflow.py` (it exists on the branch; create it if the rebase drops it), with `CliRunner` in temporary repositories as `RepoTestCase` sets up, using `os.chdir` (restored in cleanup) to choose the directory. "Outside a repository" means `configured_workflow` returns `None`: a fresh `tempfile.mkdtemp()` directory with no Chitty config in it or any parent, and `CHITTY_ROOT` unset. The test classes inherit `RepoTestCase`, which clears `CHITTY_ROOT` and the Pi session variables (`tests/support.py`), so the general guide carries no Pi warning. No property: a fixed set of seven roles, two workflows and outside a repository, each case tested. The runner cases do not compare against a captured baseline (a snapshot of guide text breaks whenever a guide changes, and the branch's merge with `main` made the baseline ambiguous, 2026-11-21 review); criterion 3 is the compatibility check. Name matching in criterion 2 uses `re.search(rf"\b{re.escape(role)}\b", help_text, re.IGNORECASE)`, not a split on whitespace, so `review,` and `Work,` count; the `Usage:` line is part of the help it checks.

## Acceptance Criteria

- [ ] In a temporary repository with `workflow = "tickets"`, for each role in `ROLE_NAMES`, `chitty guide <role>` and `chitty guide <role> TASK-1` (including `plan` and `setup`, which get the workflow message, not `does not take a ticket ID`) exit 1, print nothing on stdout, and have stderr containing `chitty guide <role> needs workflow = "runner" in the Chitty config`; and calling `guide("work", directory=<root>, workflow=w)` directly raises `ChittyError` for each `w` in `"tickets"`, `"bogus"`, `""` and `"Runner"`; this fails before the change
- [ ] Under `tickets`, `chitty guide` exits 0 and prints `managed_guide("tickets")`, and `chitty guide --help` exits 0, contains `chitty guide` and contains no role name from `ROLE_NAMES`; this fails before the change
- [ ] With `workflow = "runner"`, and outside a repository, for each role, without an ID and (for every role except `plan` and `setup`) with `TASK-1`, `chitty guide <role>` exits 0 with empty stderr and stdout equal to `src/chitty/roles/<role>.md` with `<!-- property-signals -->` replaced by the text of `property-signals.md` with `rstrip()` applied to it (the placeholder occurs only in `plan.md` and `cold-read.md`, which must show the substitution), prefixed by `Work only on Chitty ticket TASK-1.` and a blank line when the ID is given; `chitty guide --help` contains every line of the current docstring, including the paragraph starting `Work, review, cold-read and rebase accept`; with `workflow = "bogus"`, `chitty guide work` exits 1 with `workflow:` in stderr and `chitty guide --help` exits 0 with the runner docstring; `make check` passes

## Plan

Add missing exit-code and complete runner help assertions, verify tests and checks, then hand off for review.

## Notes

Cold read starting point: `refs/cold-read/TASK-334/1` (on top of TASK-332's read; mutants M1 to M4 killed). Its main files: `src/chitty/store.py`, `src/chitty/cli.py` (`_GuideCommand`), `src/chitty/run.py`, `tests/test_guide_workflow.py`; see them with `git show refs/cold-read/TASK-334/1:<path>`. It differs from the current text: its `role_workflow` falls back to runner on a broken config for role guides, which the ticket now forbids, and it also edits `tests/support.py`, which TASK-335 owns. Check it against the current criteria rather than trusting it.

Regression evidence: tests.test_guide_workflow failed before the fix on all six tickets-workflow role refusals and role-bearing help; after the implementation, the workflow and compatibility tests pass. Verification: make format && make check passed (591 Python test suites and Node tests); git status --short was empty after commit c7ed80f.

Review failed (tests): Newly discovered coverage gap: add the required baseline-capture compatibility tests for every specified case to tests/test_guide_workflow.py, checking stdout, stderr and exit code rather than comparing current output with the current implementation. No earlier review findings exist.
1: pass - tests.test_guide_workflow passes; running TestRoleGuidesUnderTickets against c7ed80f^ printed FAILED (failures=7), including all six refusals. A separate six-role probe with TASK-1 printed six roles refused.
2: pass - TestRoleGuidesUnderTickets passes; against c7ed80f^ it failed because help contained work. The managed guide assertion passed in both versions.
3: fail - tests/test_guide_workflow.py does not capture baseline output or exercise all runner and outside-repository cases and all three result fields: it omits general guide, plan/setup with ID, most outside cases, exit codes and stderr. The required fixed-case compatibility tests are missing. Independent comparison against current main printed runner 14 comparisons; differences: [] and outside 14 comparisons; differences: [] (outside simulated by patching root discovery). Broken TOML probes printed exit 1 for guide and guide work, and help exit 0 with the runner example. make format && make check passed: 588 Python tests and Node tests. Comparing to c7ed80f^ instead showed setup output differences from a separately merged main change, so baseline selection must account for that merge.

Review follow-up cannot be completed safely from the current criterion: “same output as at the commit before this change” does not identify whether the baseline is the pre-implementation parent c7ed80f^ (which includes an upstream merge and has unrelated setup-guide output differences) or the earlier implementation base before that merge. The review explicitly observed different setup output when comparing against c7ed80f^ and says baseline selection must account for the merge. Please decide which behavior is the compatibility contract (the exact pre-change tree, or behavior with unrelated merged-main changes excluded) and identify the baseline revision. Until then, snapshots risk locking in unrelated changes or testing the wrong output.

Planner, 2026-11-22: replanned against `main` (seven roles, `directory` parameter). The baseline question in the previous note is settled: no captured baseline; criterion 3, rewritten, is the compatibility check. Earlier review notes about baseline capture no longer apply.

Runner error (agent): agent timed out after 7200 seconds:

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-334`

Error output:
```text
(no output)
```

Planner, 2026-11-22: the 10:05 agent session timed out after 7200 s on its first tool call (`.venv/bin/chitty show TASK-334`); the Pi session has no result for that call, and the command returns in under a second when run by hand, so the stall was in the agent harness, not in this ticket. No work was lost (no commits or edits since the replan). Back to `doing` for another attempt. Note: this branch's own `chitty` (older than `main`) fails on branch `task-a6vmgm` with "unknown frontmatter key 'provisional'"; the runner's merge of `main` fixes that.

Regression: direct workflow test failed before the fix with unexpected workflow keyword, and passes after implementation. Earlier rebase verification showed tickets help test failing before the help fix. make check passes with 1119 tests.

Review failed (tests): Newly discovered gaps in the specified assertions; the earlier baseline-capture finding was superseded by the replan.
1: pass - make check printed Ran 1119 tests and OK; the worker recorded direct-workflow regression failure before the fix, and the earlier review recorded tickets-role tests failing before the change.
2: fail - tests/test_guide_workflow.py checks stdout but not the required exit code for either general guide or help. Assert both exit codes are zero. Earlier review recorded role-bearing help failing before the fix.
3: fail - tests/test_guide_workflow.py checks selected help phrases, omitting the repair example and other docstring text; broken-config help also lacks an exit-code assertion and complete runner-docstring comparison. Assert the specified complete help text and exit code. make check printed Ran 1119 tests and OK; runner role output cases passed. The previous baseline-capture finding no longer applies to the rewritten criterion.

Added the missing exit-code and complete docstring assertions; focused tests pass. make check fails in unrelated tests.test_property_hidden_entries: Hypothesis generates tracked chitty/tasks/.GIT and git add exits 128 on this filesystem. A maintainer must correct the unrelated property-test fixture or provide a suitable environment before the required check and review handoff can pass.

## Summary

Review follow-up assertions committed; focused tests pass, but make check is blocked by an unrelated hidden-entry property test.

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
- 2026-11-22T09:49:14Z friendly-jade-stoat: changed description, acceptance criteria; wrote the plan
- 2026-11-22T09:49:14Z friendly-jade-stoat cold-read → planning
- 2026-11-22T09:49:22Z friendly-jade-stoat: changed notes
- 2026-11-22T09:49:22Z friendly-jade-stoat planning → cold-read
- 2026-11-22T09:52:09Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T09:52:09Z friendly-jade-stoat cold-read → planning
- 2026-11-22T09:52:11Z friendly-jade-stoat planning → cold-read
- 2026-11-22T09:54:34Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T09:54:34Z friendly-jade-stoat cold-read → planning
- 2026-11-22T09:54:35Z friendly-jade-stoat planning → todo
- 2026-11-22T10:04:01Z eager-coral-wren todo → doing
- 2026-11-22T12:05:00Z eager-coral-wren: changed notes
- 2026-11-22T12:05:00Z eager-coral-wren doing → error
- 2026-11-22T13:57:28Z friendly-jade-stoat: changed notes
- 2026-11-22T13:57:28Z friendly-jade-stoat error → doing
- 2026-11-22T14:04:50Z open-dusky-vole: wrote the plan
- 2026-11-22T14:10:52Z open-dusky-vole: changed notes, summary
- 2026-11-22T14:10:52Z open-dusky-vole doing → review
- 2026-11-22T14:22:14Z brisk-silver-jay: changed acceptance criteria, notes
- 2026-11-22T14:22:14Z brisk-silver-jay review → doing
- 2026-11-22T14:28:10Z able-coral-adder: wrote the plan
- 2026-11-22T14:32:41Z able-coral-adder: changed notes, summary
- 2026-11-22T14:32:41Z able-coral-adder doing → blocked
