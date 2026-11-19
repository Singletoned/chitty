---
title: Keep the guide tests independent of this repository's `chitty.toml`
status: done
labels:
  - blocks-release
priority: high
created: 2026-11-19
---

## Description

Two guide tests run `chitty guide` with no role in the current directory, which is this checkout, so they read this repository's real `chitty.toml`:

- `test_warning_is_in_every_generated_guide` in `tests/test_guide_backticks.py` compares the no-role output with `managed_guide("runner")`. When the `0.5.0` release raised `chitty_version`, this checkout resolved to `tickets` and the test failed on `main` and every branch that merged it, with no code change.
- `tests/test_guide_pi_warning.py` (`TestGuidePiWarning.guide`) fails when this checkout's config is invalid, for example `workflow = "bogus"`.

Decisions:

- Remove the no-role case `()` from the loop in `test_warning_is_in_every_generated_guide`; keep the `work`, `review` and `plan` cases, change the expected line to `expected = guide(*args)`, and drop `managed_guide` from the import. The no-role guide is already checked in a temporary repository, for both workflows, by `test_guide_command_prints_the_repository_workflow` in `tests/test_guide_workflow_block.py`, whose expected text (`tests/fixtures/guide-before-workflow.md`) contains the backtick warning.
- `TestGuidePiWarning` inherits `RepoTestCase` (`tests/support.py`) and runs `chitty guide` after `os.chdir(self.root)`, restoring the old directory with `addCleanup`, as `CliTestCase.setUp` in `tests/test_cli.py` does, but without setting `CHITTY_ACTOR` (the test needs no identity) and without inheriting `CliTestCase`. Its `env=` arguments stay.
- The planner ran the whole suite in a throwaway copy of `main` with its `chitty.toml` changed (no `workflow` line, `chitty_version = "0.6.0"`): apart from prettier tests (no `node_modules` there), only the backticks test failed.
- Do not edit this checkout's `chitty.toml` (`AGENTS.md` forbids it on a ticket branch). Show independence in a throwaway copy outside the checkout instead.

No property: the change only removes one case and moves one test class into a temporary repository; the existing tests named above cover what remains.

## Acceptance Criteria

- [x] Recorded in a note with the commands and the test names that fail or pass: copies made with `git archive <ref> | tar -x -C <dir>`, where `<dir>` is under this worktree's `tmp/` (add `tmp/` to `.gitignore` on this branch if it is not ignored; `main` for before, the ticket branch for after), each with its `chitty.toml` edited, run from `<dir>` with the worktree's `.venv/bin/python -m unittest tests.test_guide_backticks tests.test_guide_pi_warning` and `PYTHONPATH=<dir>/src`. Before, `workflow = "tickets"` fails the backticks test and `workflow = "bogus"` fails the Pi warning test; after, both pass with `workflow = "bogus"`. Delete the copies afterwards
- [x] `test_guide_command_prints_the_repository_workflow` still passes unchanged; `make check` passes in the real worktree after `make install` (a copy has no `node_modules`, so prettier tests fail there)

## Plan

Drop the no-role case from the backticks guide test and expected managed_guide import; isolate Pi warning CLI invocation in RepoTestCase temporary repository. Verify before/after config independence with archived copies, then make check and commit implementation.

## Notes

Changed the tests as planned. Verification: `PYTHONPATH=src .venv/bin/python -m unittest tests.test_guide_backticks tests.test_guide_pi_warning tests.test_guide_workflow_block` passed (26 tests); `make check` passed all 702 tests, formatting, lint, and type checks. Its test output includes expected diagnostics from subprocess fixtures. I did not run the specified archived-copy validation under `/private/tmp/claude-501/`: the session instruction limits file creation to this worktree. Thus the separate before/after altered-config proof remains unverified. Commit: a860b871 (Task: TASK-413).

Review failed (integration): merging `main` conflicts in `tests/test_guide_backticks.py`.

The required acceptance-criterion 1 validation cannot be run under the active worktree boundary: it explicitly requires creating two archived copies under /private/tmp/claude-501/, while the session instruction says to create files only inside this ticket worktree. The earlier attempt correctly left it unrun; I did not create any files outside the worktree. Please decide whether to revise the criterion to permit temporary copies under this worktree (or explicitly authorize the specified outside path) before implementation can be returned to review. After merging main, resolved the conflict in tests/test_guide_backticks.py by retaining only the role cases and adapting expected output to guide(*args, directory=Path.cwd()). make check passed: 714 suites/tests, ruff format, ruff, and pyright; test_guide_command_prints_the_repository_workflow is included in that full suite. Commit: 576797ea.

Planning 2026-11-19: the worker was right; criterion 1 asked for copies outside the worktree, which workers may not create. The copies now go in this worktree's ignored `tmp/`. The code change and its tests are done; only this evidence is missing. No new cold read: only the copy location changed.

Archived-copy validation: `git archive main | tar -x -C tmp/task-413-before` and `git archive HEAD | tar -x -C tmp/task-413-after`; edited chitty.toml workflows and deleted copies afterward. Before, workflow = "tickets": `PYTHONPATH=tmp/task-413-before/src .venv/bin/python -m unittest tests.test_guide_backticks tests.test_guide_pi_warning` failed `TestBacktickGuideWarning.test_warning_is_in_every_generated_guide` for args=(). Before, workflow = "bogus": `PYTHONPATH=tmp/task-413-before/src .venv/bin/python -m unittest tests.test_guide_pi_warning` failed `TestGuidePiWarning.test_pi_without_identity_is_warned` because guide exited on invalid workflow. After, workflow = "bogus": `PYTHONPATH=tmp/task-413-after/src .venv/bin/python -m unittest tests.test_guide_backticks tests.test_guide_pi_warning` passed (8 tests). Real worktree `make check` passed formatting, ruff, pyright, and all 714 tests, including `test_guide_command_prints_the_repository_workflow`. Validation scratch copies removed; `tmp/` ignored in commit a38ca7f8.

Reviewed: previous merge conflict and archive-location obstacle resolved; no new findings.
1: pass - repeated git archive main and HEAD into ignored tmp copies, edited workflows and ran both unittest modules with PYTHONPATH set to each copy: main tickets failed the backticks test, main bogus failed that test and test_pi_without_identity_is_warned, HEAD bogus printed OK (8 tests). Copies deleted.
2: pass - unchanged test_guide_command_prints_the_repository_workflow printed OK (1 test); make check printed OK (725 tests), ruff and pyright clean. Earlier worker notes record make install and passing checks.

## Summary

Handoff: removed config-dependent no-role guide assertion and isolated Pi warning guide invocation in a temporary repository. Archived before/after altered-config validation and full make check passed. No follow-up identified.

## History

- 2026-11-19T10:01:38Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:51Z quick-ginger-lapwing: changed labels
- 2026-11-19T11:22:35Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:22:35Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:24:33Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:24:37Z quick-ginger-lapwing: changed title, description, acceptance criteria
- 2026-11-19T11:24:37Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:26:06Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:26:09Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:26:09Z quick-ginger-lapwing planning → todo
- 2026-11-19T11:30:51Z golden-hazel-raven todo → doing
- 2026-11-19T11:31:54Z golden-hazel-raven: wrote the plan
- 2026-11-19T11:33:18Z golden-hazel-raven: changed notes
- 2026-11-19T11:33:21Z golden-hazel-raven: changed summary
- 2026-11-19T11:33:21Z golden-hazel-raven doing → review
- 2026-11-19T13:19:41Z able-ochre-badger: changed notes
- 2026-11-19T13:19:41Z able-ochre-badger review → doing
- 2026-11-19T13:23:59Z plucky-fawn-dormouse: changed owner, notes
- 2026-11-19T13:23:59Z plucky-fawn-dormouse doing → planning
- 2026-11-19T13:53:08Z quick-ginger-lapwing: changed acceptance criteria, notes
- 2026-11-19T13:53:08Z quick-ginger-lapwing planning → todo
- 2026-11-19T13:57:45Z daring-ochre-lapwing todo → doing
- 2026-11-19T14:02:55Z daring-ochre-lapwing: changed notes, summary; ticked acceptance criteria
- 2026-11-19T14:02:55Z daring-ochre-lapwing doing → review
- 2026-11-19T14:12:26Z jolly-jade-newt: changed notes
- 2026-11-19T14:12:26Z jolly-jade-newt review → done
