---
title: Move `planning` tickets to `to-plan` when repository setup upgrades
status: review
labels:
  - needs-minor
depends_on:
  - TASK-10032
  - TASK-10029
parent: TASK-10026
created: 2026-11-25
moved_from: TASK-QZ7SD8
---

## Description

Part of `TASK-10026`, after `TASK-10032`. Once `planning` means "a planner has it", every ticket left in `planning` from before the split would look claimed, by whichever session last moved it there, usually one long gone (on 2026-11-25 this repository had 20 `planning` tickets, one with an owner). They should become `to-plan`, once, without anyone running a command.

Change, in `init_repo` in `src/chitty/store.py`, in the existing-config branch where `recorded_version` is read: when `recorded_version` differs from `CHITTY_VERSION` (the gate the workflow upgrade already uses) and is missing or not later than a new constant `LAST_SHARED_PLANNING_VERSION` in `src/chitty/config.py` (next to `LAST_RUNNER_DEFAULT_VERSION`, compared with `version_key` the same way), rewrite every unarchived ticket in each configured context whose status is `planning`: status `to-plan`, `owner` removed, and a History transition `planning → to-plan` by actor `chitty`. Add the rewritten files to `written`, so they land in the same `chitty: upgrade repository setup` commit. Set the constant to `__version__` in `src/chitty/__init__.py` on `main` when you start (`0.8.0` on 2026-11-25), since this branch must not change `__version__`.

The automatic upgrade (`Repo._check_setup_version`) skips linked worktrees, so this runs in the main checkout only. A `planning` ticket on an unlanded branch is not migrated; its claim can be released with `-s to-plan --note`.

Out of scope: archived tickets, `cold-read` tickets, and the guides.

A repository whose setup records exactly `0.8.0` is migrated on the first release after this lands, not by a branch build that also reports `0.8.0`; that is intended.

Tests, in `tests/test_init_workflow.py` (no property: three fixed cases, each tested). Run at the real `CHITTY_VERSION`, not through `TestUpgradeWorkflow.invoke`, which patches the running version to `0.5.1`. Call `init_repo(root, False, "chitty: upgrade repository setup")` directly, as `Repo._check_setup_version` does (plain `chitty init` does not commit). Case 1: `chitty.toml` records `chitty_version = "0.7.1"`, with one `planning` ticket (with an owner), one `todo` ticket and one archived `planning` ticket, all committed. Afterwards the `planning` ticket is `to-plan` with no owner and a `chitty planning → to-plan` History line, the other two files are byte-identical, and the moved file is in `init_repo`'s returned paths and in `git log -1 --name-only`. Case 2: calling `init_repo` again changes nothing. Case 3: with `chitty_version` set to `CHITTY_VERSION`, a `planning` ticket is left as it is.

## Acceptance Criteria

- [ ] The three cases in `tests/test_init_workflow.py` pass, and the first fails before the change. Regression tests: the other two cases
- [ ] `make check` passes

## Plan

Add fixed upgrade tests at the real version, verify migration fails before implementation, then migrate active planning tickets at the version boundary using existing task parsing and history methods. Preserve rollback and include migrated paths in the upgrade commit; run formatting and checks.

## Notes

Before the fix, the three fixed tests produced one failure: the old setup retained planning instead of to-plan; the two regression cases passed.

## Summary

Setup upgrades migrate active planning tickets from shared-planning versions to to-plan, clear owners, and commit history changes with setup. Fixed tests verify migration, repeat upgrade, and current-version behavior; make check passes.

## History

- 2026-11-25T23:07:24Z golden-coral-stoat → backlog
- 2026-11-25T23:07:42Z golden-coral-stoat: changed description, acceptance criteria
- 2026-11-25T23:10:16Z golden-coral-stoat: changed dependencies, description
- 2026-11-25T23:12:35Z golden-coral-stoat backlog → todo
- 2026-11-25T23:12:53Z golden-coral-stoat: renumbered from TASK-QZ7SD8
- 2026-11-26T02:35:50Z rosy-dusky-vole todo → doing
- 2026-11-26T02:38:38Z rosy-dusky-vole: wrote the plan
- 2026-11-26T02:39:15Z rosy-dusky-vole: changed notes
- 2026-11-26T02:42:21Z rosy-dusky-vole: changed summary
- 2026-11-26T02:44:44Z rosy-dusky-vole doing → review
