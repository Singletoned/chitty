---
title: Add an optional `landing_check` setting that replaces `check` when landing
status: doing
priority: medium
created: 2026-11-19
---

## Description

`chitty run` uses one `check` command both to validate a ticket worktree before an agent session (`_run_check` in `src/chitty/run.py`) and to check the rebased branch before landing (`_landing_check`, called from `_land_locked`). A repository may want a slower, stricter check only at landing, for example `TASK-429`'s `sh scripts/check_linux.sh`, which runs `make check` in a Linux container: running it before every agent session would slow every start. Add an optional `landing_check` setting that replaces `check` on landing only. Unset, landing runs `check` as today, so existing repositories see no change.

Decisions:

- `RepoConfig` in `src/chitty/config.py` gets `landing_check: str | None = None`, next to `check`, and joins `setup`, `check` and `error_reporter` in the `_command` validator, so a blank value fails to load with `<path>: landing_check: must not be empty`. Today the key is unknown: Chitty warns `ignoring unknown configuration key(s) landing_check` and ignores it.
- Add a pure function `landing_command(check: str | None, landing_check: str | None) -> str` in `src/chitty/config.py`: `landing_check` when it is not `None`, else `check`; when both are `None`, raise `ChittyError` naming `check`. In `src/chitty/run.py`, both landing callers pass `landing_command(main_repo.config.check, main_repo.config.landing_check)` to `_land` in place of `check`: `_land_pending` (`_land(main_repo, worktree, action, setup, check)` near line 336) and the review path in `_run_ticket` (near line 534). The check before an agent session keeps using `check`. `_preflight` still requires `check`, and runs before `_land_pending`, so keep the existing `assert setup is not None` and `assert check is not None` lines in both callers. Add `landing_command` first raising `NotImplementedError`, so its tests fail on behaviour rather than at import.
- Documentation: in `docs/plan/config.md`, change the `# check = ...` comment of the example to `# check = "make check" # validates the worktree before the agent; also on landing unless landing_check is set`, add after the `# check = ...` line of the example `# landing_check = "sh scripts/check_linux.sh" # replaces check on landing only`, and in `README.md` add one sentence after the `chitty run` requirements (near line 155) saying `landing_check` optionally replaces `check` when landing. Leave `INITIAL_CONFIG` unchanged.

Tests, in a new `tests/test_landing_check_setting.py`:

- `landing_command`: the four combinations of `check` in {`"a"`, `None`} and `landing_check` in {`"b"`, `None`}: `"a", None` gives `"a"`; `"a", "b"` and `None, "b"` give `"b"`; `None, None` raises `ChittyError` (assert with `assertRaisesRegex(ChittyError, "check")`); and `"a", ""` gives `""`, which catches an implementation written as `landing_check or check` (config validation rejects a blank value, so only the pure function sees it). No property: a fixed set of five, each listed and tested.
- Review path, inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py`. Write a script that appends its second argument and a newline to the file named by its first. In `chitty.toml`, replace the fixture's `check = ...` line (a regular expression on `^check = .*$`, multiline) with `check = "<python> <script> <logs>/calls check"`; for the set case add, on the line after it, `landing_check = "<python> <script> <logs>/calls landing"`. Keys must go before the first `[table]`, or TOML puts them in that table. Commit the change on `main` (`git commit -am`), then `branch_for_review()`, then `run_cli("run", "--mode", "review")`. Set: the last output line is `TASK-1: review → done` and `calls` reads exactly `check\nlanding\n`. Unset: `calls` reads exactly `check\ncheck\n`. A probe of the unset case against today's code on 2026-11-19 printed `TASK-1: review → done` and `check\ncheck\n`.
- Pending path, inheriting `LandingTestCase` from `tests/test_landing.py`. Its `setUp` writes `check = "true"`; replace that with `check = "false"` and add `landing_check = "<python> <script> <logs>/calls landing"` before the first table, commit on `main`, then in `self.worktree` run `git merge --ff-only --quiet main` so the branch carries the same `chitty.toml`, then `finish_ticket()` and `_land_pending(Repo.open(self.root))`. It returns a result for `TASK-1`, `calls` reads exactly `landing\n`, and the worktree is gone. Against today's code it raises `landing check exited with status 1`.
- Loading: with `landing_check = "  "` at the top level, `chitty list` exits 1 with `landing_check: must not be empty` on stderr; with `landing_check = "true"`, `chitty list` prints no `unknown configuration key` warning.

Out of scope: setting `landing_check` in this repository's `chitty.toml` (a later ticket, on `main`), `INITIAL_CONFIG`, and a separate landing `setup`.

## Acceptance Criteria

- [x] `tests/test_landing_check_setting.py` has the five `landing_command` cases from the Description, and they pass; a note records that they fail while `landing_command` raises `NotImplementedError`
- [x] The review-path test passes for both cases as described: set gives `calls` exactly `check\nlanding\n`, unset gives `check\ncheck\n`; a note records that the set case fails against `src/chitty/run.py` without the change (`calls` is `check\ncheck\n`)
- [x] The pending-path test passes as described (`calls` exactly `landing\n`, worktree removed); a note records that it fails against `src/chitty/run.py` without the change with `landing check exited with status 1`, and that it also fails with only the review-path caller changed
- [x] The loading test passes: with a blank `landing_check`, `chitty list` exits 1 with `landing_check: must not be empty`; with `landing_check = "true"` it prints no `unknown configuration key` warning; a note records that the blank case fails against `src/chitty/config.py` without the change
- [x] `docs/plan/config.md` and `README.md` describe `landing_check` as the Description says; `make check` passes

## Plan

Add landing_check configuration validation and landing_command selection, route both landing paths through it while preserving check for preflight/worktree checks, and add focused regression tests for selection, review/pending landing, and config loading. Update config and README documentation, run required red/green tests and make check, then commit implementation with Task: TASK-430.

## Notes

Confirmed all five landing_command regression cases fail while the function raises NotImplementedError (python -m unittest tests.test_landing_check_setting). The required test-first failure is recorded.

Integration regressions verified red with both landing callers temporarily restored to pass check: review landing recorded check/check instead of check/landing; pending landing raised `landing check exited with status 1`. With both callers changed, review set and unset cases pass with check/landing and check/check, and pending landing passes with landing and removes the worktree. The blank-setting loading test rejects with `landing_check: must not be empty`; the nonblank setting emits no unknown-key warning. `make check` passes.

## Summary

Implemented optional landing_check selection for review and pending landing while preserving check before agent sessions. Added five selection cases, config-loading coverage, review and pending integration regressions, and config/README docs. Verified with `python -m unittest tests.test_landing_check_setting` and `make check` (ruff, pyright, 775 suites). No follow-up required.

## History

- 2026-11-19T18:41:20Z daring-amber-kestrel → planning
- 2026-11-19T18:41:38Z daring-amber-kestrel planning → cold-read
- 2026-11-19T18:42:29Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T18:42:29Z daring-amber-kestrel cold-read → planning
- 2026-11-19T18:42:40Z daring-amber-kestrel planning → cold-read
- 2026-11-19T18:43:51Z daring-amber-kestrel: changed description, acceptance criteria
- 2026-11-19T18:43:51Z daring-amber-kestrel cold-read → planning
- 2026-11-19T18:43:56Z daring-amber-kestrel planning → todo
- 2026-11-19T20:35:29Z witty-lilac-falcon todo → doing
- 2026-11-19T20:41:56Z brisk-white-otter: wrote the plan
- 2026-11-19T20:42:46Z brisk-white-otter: changed notes
- 2026-11-19T20:49:51Z brisk-white-otter: changed notes, summary; ticked acceptance criteria
