---
title: Resolve a config recorded at `0.5.0` or earlier with no `workflow` to the runner
status: planning
labels:
  - blocks-release
priority: high
created: 2026-11-19
---

## Description

`resolve_workflow` in `src/chitty/config.py` decides the workflow of a config with no `workflow` line from its recorded `chitty_version`: older than `FIRST_WORKFLOW_VERSION` (`"0.5.0"`) is `runner`, otherwise `tickets`. Release `0.5.0` was published before `chitty init` could write `workflow = "runner"` on upgrade (`TASK-331`), so it raised existing runner repositories to `0.5.0`, which then resolved to `tickets` and lost `chitty run` and `chitty next` (seen 2026-11-19 in this repository and in `echonomicon`). `0.5.0` has been yanked, so every config recorded at `0.5.0` was raised by that release, not set up for the tickets workflow. Decided with the owner 2026-11-19: such configs count as runner.

Decisions:

- Replace `FIRST_WORKFLOW_VERSION = "0.5.0"` with `LAST_RUNNER_DEFAULT_VERSION = "0.5.0"`: a missing `workflow` resolves to `runner` when the recorded version is `None`, unparsable (as today), or at most `0.5.0`, and to `tickets` when later.
- Compare versions with trailing zero parts dropped, inside `resolve_workflow` only, so `0.5`, `0.5.0` and `0.5.0.0` are the same version (today `version_key` gives `(0, 5, 0, 0) > (0, 5, 0)`). Leave `version_key` and `check_setup_version` unchanged.
- An explicit `workflow` line is returned as is (unchanged).
- Update `docs/plan/config.md` (the paragraph naming `FIRST_WORKFLOW_VERSION`) to describe the new boundary and why.

Out of scope: writing `workflow` during `chitty init` (`TASK-331` and its split pieces).

Tests: in `tests/test_config_workflow.py`, using Hypothesis, the repository's property-testing tool. Update the oracle `expected_workflow` and the `@example`s of `test_missing_workflow_follows_setup_version`; keep its `VERSIONS` strategy (none, one to four dot-separated non-negative integers, any text). The code exists, so the evidence of failing without the change is wrong versions, run by hand: today's code (`<` against `0.5.0`); `<=` without dropping trailing zeros; and comparing the version strings as text. Record in a note which test each fails.

## Acceptance Criteria

- [ ] Property (Hypothesis): for any version drawn from `VERSIONS`, `resolve_workflow(None, version)` is `runner` when the version is `None`, unparsable, or numerically at most `0.5.0` once trailing zero parts are dropped, and `tickets` otherwise; `@example`s include `0.5`, `0.5.0`, `0.5.0.0`, `0.5.0.1`, `0.5.1` and `0.4.9`. Today it fails on `0.5.0`
- [ ] A `RepoTestCase` config with `chitty_version = "0.5.0"` and no `workflow` or `review` line loads with `workflow` `runner` and `review` true; with `chitty_version = "0.5.1"` it loads with `tickets` and `review` false
- [ ] The note records each wrong version in the Tests paragraph and the test it fails; `docs/plan/config.md` describes the new boundary; `make check` passes

## History

- 2026-11-19T10:39:34Z quick-ginger-lapwing → planning
