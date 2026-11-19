---
title: Add an optional `landing_check` setting that replaces `check` when landing
status: planning
priority: medium
created: 2026-11-19
---

## Description

`chitty run` uses one `check` command both to validate a ticket worktree before an agent session (`_run_check` in `src/chitty/run.py`) and to check the rebased branch before landing (`_landing_check`, called from `_land_locked`). A repository may want a slower, stricter check only at landing, for example `TASK-429`'s `sh scripts/check_linux.sh`, which runs `make check` in a Linux container: running it before every agent session would slow every start. Add an optional `landing_check` setting that replaces `check` on landing only. Unset, landing runs `check` as today, so existing repositories see no change.

Decisions:

- `RepoConfig` in `src/chitty/config.py` gets `landing_check: str | None = None`, next to `check`, and joins `setup`, `check` and `error_reporter` in the `_command` validator, so a blank value fails to load with `<path>: landing_check: must not be empty`. Today the key is unknown: Chitty warns `ignoring unknown configuration key(s) landing_check` and ignores it.
- Add a pure function `landing_command(check: str | None, landing_check: str | None) -> str` in `src/chitty/config.py`: `landing_check` when it is not `None`, else `check`; when both are `None`, raise `ChittyError` naming `check`. In `src/chitty/run.py`, both landing callers pass `landing_command(main_repo.config.check, main_repo.config.landing_check)` to `_land` in place of `check`: `_land_pending` (`_land(main_repo, worktree, action, setup, check)` near line 336) and the review path in `_run_ticket` (near line 534). The check before an agent session keeps using `check`. `_preflight` still requires `check`.
- Documentation: in `docs/plan/config.md`, add after the `# check = ...` line of the example `# landing_check = "sh scripts/check_linux.sh" # replaces check on landing only`, and in `README.md` add one sentence after the `chitty run` requirements (near line 155) saying `landing_check` optionally replaces `check` when landing. Leave `INITIAL_CONFIG` unchanged.

Tests, in a new `tests/test_landing_check_setting.py`:

- `landing_command`: the four combinations of `check` in {`"a"`, `None`} and `landing_check` in {`"b"`, `None`}: `"a", None` gives `"a"`; `"a", "b"` and `None, "b"` give `"b"`; `None, None` raises `ChittyError`. No property: a fixed set of four, each listed and tested.
- Review path, inheriting `ReviewMergeTestCase` from `tests/test_review_merge.py`. Write a script that appends its second argument and a newline to the file named by its first. In `chitty.toml`, replace the fixture's `check = ...` line (a regular expression on `^check = .*$`, multiline) with `check = "<python> <script> <logs>/calls check"`; for the set case add, on the line after it, `landing_check = "<python> <script> <logs>/calls landing"`. Keys must go before the first `[table]`, or TOML puts them in that table. Commit the change on `main` (`git commit -am`), then `branch_for_review()`, then `run_cli("run", "--mode", "review")`. Set: the last output line is `TASK-1: review → done` and `calls` reads exactly `check\nlanding\n`. Unset: `calls` reads exactly `check\ncheck\n`. A probe of the unset case against today's code on 2026-11-19 printed `TASK-1: review → done` and `check\ncheck\n`.
- Pending path, inheriting `LandingTestCase` from `tests/test_landing.py`. Its `setUp` writes `check = "true"`; replace that with `check = "false"` and add `landing_check = "<python> <script> <logs>/calls landing"` before the first table, commit on `main`, then in `self.worktree` run `git merge --ff-only --quiet main` so the branch carries the same `chitty.toml`, then `finish_ticket()` and `_land_pending(Repo.open(self.root))`. It returns a result for `TASK-1`, `calls` reads exactly `landing\n`, and the worktree is gone. Against today's code it raises `landing check exited with status 1`.
- Loading: with `landing_check = "  "` at the top level, any command fails with `landing_check: must not be empty`; with `landing_check = "true"`, `chitty list` prints no `unknown configuration key` warning.

Out of scope: setting `landing_check` in this repository's `chitty.toml` (a later ticket, on `main`), `INITIAL_CONFIG`, and a separate landing `setup`.

## Acceptance Criteria

- [ ] `tests/test_landing_check_setting.py` has the four `landing_command` cases from the Description, and they pass
- [ ] The review-path test passes for both cases as described: set gives `calls` exactly `check\nlanding\n`, unset gives `check\ncheck\n`; a note records that the set case fails against `src/chitty/run.py` without the change (`calls` is `check\ncheck\n`)
- [ ] The pending-path test passes as described (`calls` exactly `landing\n`, worktree removed); a note records that it fails against `src/chitty/run.py` without the change with `landing check exited with status 1`, and that it also fails with only the review-path caller changed
- [ ] The loading test passes: blank `landing_check` fails with `landing_check: must not be empty`, and a set `landing_check` gives no `unknown configuration key` warning
- [ ] `docs/plan/config.md` and `README.md` describe `landing_check` as the Description says; `make check` passes

## History

- 2026-11-19T18:41:20Z daring-amber-kestrel → planning
