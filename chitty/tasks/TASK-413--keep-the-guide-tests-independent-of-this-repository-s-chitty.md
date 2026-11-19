---
title: Keep the guide tests independent of this repository's `chitty.toml`
status: planning
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

- Remove the no-role case `()` from the loop in `test_warning_is_in_every_generated_guide`; keep the `work`, `review` and `plan` cases. The no-role guide is already checked in a temporary repository, for both workflows, by `test_guide_command_prints_the_repository_workflow` in `tests/test_guide_workflow_block.py`, whose expected text (`tests/fixtures/guide-before-workflow.md`) contains the backtick warning.
- `TestGuidePiWarning` inherits `RepoTestCase` (`tests/support.py`) and runs `chitty guide` after `os.chdir(self.root)`, restoring the old directory with `addCleanup`, as `CliTestCase.setUp` in `tests/test_cli.py` does. Its `env=` arguments stay.
- The planner ran the whole suite in a throwaway copy of `main` with its `chitty.toml` changed (no `workflow` line, `chitty_version = "0.6.0"`): apart from prettier tests (no `node_modules` there), only the backticks test failed.
- Do not edit this checkout's `chitty.toml` (`AGENTS.md` forbids it on a ticket branch). Show independence in a throwaway copy outside the checkout instead.

No property: the change only removes one case and moves one test class into a temporary repository; the existing tests named above cover what remains.

## Acceptance Criteria

- [ ] Recorded in a note: in a throwaway copy of the worktree outside the checkout, with `workflow = "bogus"` in the copy's `chitty.toml`, `tests.test_guide_backticks` and `tests.test_guide_pi_warning` both pass after the change; before it, with `workflow = "tickets"` the backticks test fails, and with `workflow = "bogus"` the Pi warning test fails
- [ ] `test_guide_command_prints_the_repository_workflow` still passes unchanged; `make check` passes

## History

- 2026-11-19T10:01:38Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:51Z quick-ginger-lapwing: changed labels
- 2026-11-19T11:22:35Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:22:35Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:24:33Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:24:37Z quick-ginger-lapwing: changed title, description, acceptance criteria
- 2026-11-19T11:24:37Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:26:06Z quick-ginger-lapwing cold-read → planning
