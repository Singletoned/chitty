---
title: Guard provisional renumbering preflight and report bad paths
status: planning
depends_on:
  - TASK-391
parent: TASK-391
created: 2026-11-21
---

## Description

Add rejection paths to the read-only planner `Repo._plan_provisional_renumbering` in `src/chitty/store.py` (landed by `TASK-391`). `TASK-517` is the writer that will use it. No CLI command, no writes.

Decisions:

- Branch guard, first thing in the planner, before any discovery: if `git.is_repository(self.root)` (call `git` directly, not the cached `Repo` helpers) and `git.current_branch(self.root) != self._main_branch()`, raise new `ProvisionalOffMain(ChittyError)`, defined in `src/chitty/errors.py`, with the message `provisional tickets are renumbered on <main>; current branch is <branch>`, where `<branch>` is the branch name or `detached HEAD`. `git.current_branch` returns `None` when detached, so detached HEAD is off main. Outside Git the planner behaves as today.
- Do not call `_prepare_write` and do not change allocation (`plan_renumbering`, `_used_numbers`).
- Duplicate guard: after the disk scan and before `plan_renumbering`, if any candidate ID has two or more scanned disk paths, raise `ChittyError(f"{id} is used by more than one file: {first}, {second}")` with the first two such paths in scan order. Today `plan_renumbering` raises `duplicate provisional task ID <id>` with no paths.
- A malformed file with a valid ticket filename already raises `<path>: <error>` from `_load`; keep that.

Tests: new `tests/test_provisional_preflight_errors.py`, a `RepoTestCase` with real Git, reusing the `file` and `snapshot` helpers style of `tests/test_provisional_preflight.py`. Setup: `git init -b main`, local author, commit a valid provisional `chitty/tasks/TASK-AAAAAA--example.md`, then delete the `chitty_version` line from `chitty.toml` and commit, so setup is stale (a call to `_prepare_write` would act on it). Take the snapshot (HEAD, `.git/index` bytes, bytes of every `chitty/**/*.md` and `chitty.toml`) after each setup and before the call.

- Off main: `git switch -c feature`; and separately `git checkout --detach`. Each raises `ProvisionalOffMain` whose message contains `feature` or `detached HEAD` respectively.
- On main, malformed: also commit `chitty/tasks/TASK-BAAAAA--bad.md` holding `not a ticket`; the planner raises `ChittyError` whose message starts with that file's path.
- On main, duplicate: also commit `chitty/tasks/archive/TASK-AAAAAA--copy.md`, a valid provisional ticket; the planner raises `ChittyError` whose message contains both paths.

No property: a small fixed set of Git states and files, each listed here. Before implementing, run the off-main and duplicate tests against the unguarded planner and confirm they fail; the malformed test is a regression guard and may already pass. Then implement, run the new tests and `make check`.

## Acceptance Criteria

- [ ] With stale setup and eligible work, a branch off configured main and detached HEAD each raise `ProvisionalOffMain`, before any writes; compare HEAD, index and file bytes.
- [ ] On main, an unparseable ticket or duplicate provisional candidate each refuses the whole plan with the bad path or both duplicate paths respectively, with HEAD, index and files unchanged.

## History

- 2026-11-21T18:44:40Z eager-ginger-adder → backlog
- 2026-11-21T18:45:14Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:45:14Z eager-ginger-adder backlog → planning
- 2026-11-21T23:00:01Z lively-zinc-newt: changed description
