---
title: Resolve a config recorded at `0.5.0` or earlier with no `workflow` to the runner
status: todo
labels:
  - blocks-release
priority: high
created: 2026-11-19
---

## Description

`resolve_workflow` in `src/chitty/config.py` decides the workflow of a config with no `workflow` line from its recorded `chitty_version`: older than `FIRST_WORKFLOW_VERSION` (`"0.5.0"`) is `runner`, otherwise `tickets`. Release `0.5.0` was published before `chitty init` could write `workflow = "runner"` on upgrade (`TASK-331`), so it raised existing runner repositories to `0.5.0`, which then resolved to `tickets` and lost `chitty run` and `chitty next` (seen 2026-11-19 in this repository and in `echonomicon`). `0.5.0` has been yanked, so every config recorded at `0.5.0` was raised by that release, not set up for the tickets workflow. Decided with the owner 2026-11-19: such configs count as runner.

Decisions:

- Replace `FIRST_WORKFLOW_VERSION = "0.5.0"` with `LAST_RUNNER_DEFAULT_VERSION = "0.5.0"`: a missing `workflow` resolves to `runner` when the recorded version is `None`, unparsable, or at most `0.5.0`, and to `tickets` when later. Unparsable means `version_key` raises `ChittyError`, as today; its lenient parsing stays (`1_0` is 10, `+5` is 5).
- Compare with trailing zero parts dropped from the parsed tuple, inside `resolve_workflow` only, so `0.5`, `0.5.0`, `0.5.00` and `0.5.0.0` are the same version, and `0`, `0.0` are below it (today `(0, 5, 0, 0) > (0, 5, 0)`). `version_key`, `check_setup_version` and the setup-version warning in `src/chitty/cli.py` are unchanged, so they still treat `0.5.0.0` as newer than `0.5.0`; accepted.
- An explicit `workflow` line is returned as is (unchanged).
- Accepted consequence: `__version__` on `main` is `0.5.0` until the next release, so until then a new `chitty init` from `main` resolves to `runner` (`src/chitty/store.py` near line 1395 calls `resolve_workflow(None, CHITTY_VERSION)`). Released `0.5.1` and later give new setups `tickets`, as `TASK-330` intended.
- Update `docs/plan/config.md` (the paragraph naming `FIRST_WORKFLOW_VERSION`) to describe the new boundary and why.

Out of scope: writing `workflow` during `chitty init` (`TASK-331` and its split pieces).

Tests, in `tests/test_config_workflow.py`, with Hypothesis, the repository's property-testing tool:

- Rewrite the oracle `expected_workflow` independently of the code under test: split on `.`, convert each part with `int` (any `ValueError` means unparsable, `runner`), drop trailing zero parts itself, and give `runner` when the tuple is at most `(0, 5)` (`<=`), else `tickets`. It must not call `resolve_workflow`, `version_key` or a new helper from `src/chitty/config.py`.
- `test_missing_workflow_follows_setup_version` keeps its `VERSIONS` strategy and gains `@example`s for the boundary, because unbounded integers almost never draw it: `0.4.9`, `0.5`, `0.5.0`, `0.5.00`, `0.5.0.0`, `0.5.0.1`, `0.5.1`, `0.10`, `0`, `0.0`.
- In `TestWorkflowConfig.test_missing_workflow_resolves_from_setup_version` (around line 75), the `0.5.0` case now expects `runner`; add a `0.5.1` case expecting `tickets`. Assert `review` as well as `workflow` for both (true for `0.5.0`, false for `0.5.1`), and load with `load_repo_config(self.root)` as the existing loop does: `Repo` refuses a recorded version above the installed `0.5.0` (`check_setup_version`). `TestFixtureConfig` keeps an explicit `workflow` line, so it does not cover the boundary. Build each config with the existing `config_text` helper, which removes the fixture's `workflow = "runner"` line; the fixture has no `review` line.
- The code exists, so evidence of failing without the change comes from wrong versions of `resolve_workflow`, run by hand against the updated tests: today's code (`<` against `0.5.0`); `<=` against `(0, 5, 0)` without dropping trailing zeros; and comparing the version string with `"0.5.0"` as text.

## Acceptance Criteria

- [ ] Property (Hypothesis): for any version drawn from `VERSIONS` and every listed `@example`, `resolve_workflow(None, version)` equals the independent oracle described in Tests; run against today's code, the updated test fails on `0.5.0`
- [ ] In `TestWorkflowConfig`, a config with `chitty_version = "0.5.0"` and no `workflow` or `review` line loads with `workflow` `runner` and `review` true; with `0.5.1` it loads with `tickets` and `review` false
- [ ] A note gives one line for each of the three wrong versions in Tests: the wrong version, a version it gets wrong, and the test that fails; `docs/plan/config.md` describes the new boundary; `make check` passes

## History

- 2026-11-19T10:39:34Z quick-ginger-lapwing → planning
- 2026-11-19T10:39:45Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T10:42:05Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T10:42:05Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T10:42:27Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T10:48:54Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T10:48:58Z quick-ginger-lapwing: changed description
- 2026-11-19T10:48:58Z quick-ginger-lapwing planning → todo
