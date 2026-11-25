---
title: Move `planning` tickets to `to-plan` when repository setup upgrades
status: backlog
labels:
  - needs-minor
depends_on:
  - TASK-SYR88D
parent: TASK-10026
created: 2026-11-25
provisional: true
---

## Description

Part of `TASK-10026`, after `TASK-SYR88D`. Once `planning` means "a planner has it", every ticket left in `planning` from before the split would look claimed, by whichever session last moved it there, usually one long gone (on 2026-11-25 this repository had 20 `planning` tickets, one with an owner). They should become `to-plan`, once, without anyone running a command.

Change, in `init_repo` in `src/chitty/store.py`, in the existing-config branch where `recorded_version` is read: when `recorded_version` differs from `CHITTY_VERSION` (the gate the workflow upgrade already uses) and is missing or not later than a new constant `LAST_SHARED_PLANNING_VERSION` in `src/chitty/config.py` (next to `LAST_RUNNER_DEFAULT_VERSION`, compared with `version_key` the same way), rewrite every unarchived ticket in each configured context whose status is `planning`: status `to-plan`, `owner` removed, and a History transition `planning → to-plan` by actor `chitty`. Add the rewritten files to `written`, so they land in the same `chitty: upgrade repository setup` commit. Set the constant to `__version__` in `src/chitty/__init__.py` on `main` when you start (`0.8.0` on 2026-11-25), since this branch must not change `__version__`.

The automatic upgrade (`Repo._check_setup_version`) skips linked worktrees, so this runs in the main checkout only. A `planning` ticket on an unlanded branch is not migrated; its claim can be released with `-s to-plan --note`.

Out of scope: archived tickets, `cold-read` tickets, and the guides.

Tests, in `tests/test_init_workflow.py` (no property: three fixed cases, each tested): a repository whose `chitty.toml` records `chitty_version = "0.7.1"`, with one `planning` ticket (with an owner), one `todo` ticket and one archived `planning` ticket, committed; run `chitty init`. The `planning` ticket is now `to-plan` with no owner and a `chitty planning → to-plan` History line, the other two files are byte-identical, and `git log -1 --name-only` lists the moved file in the upgrade commit. Running `chitty init` again changes nothing. With `chitty_version` set to the running `CHITTY_VERSION`, a `planning` ticket is left as it is.

## Acceptance Criteria

- [ ] The three cases in `tests/test_init_workflow.py` pass, and the first fails before the change. Regression tests: the other two cases
- [ ] `make check` passes

## History

- 2026-11-25T23:07:24Z golden-coral-stoat → backlog
- 2026-11-25T23:07:42Z golden-coral-stoat: changed description, acceptance criteria
