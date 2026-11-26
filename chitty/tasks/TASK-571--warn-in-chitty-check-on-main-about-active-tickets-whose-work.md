---
title: Warn in `chitty check` on `main` about active tickets whose work is on `main` but are not done
status: cold-read
depends_on:
  - TASK-358
  - TASK-572
  - TASK-10002
created: 2026-11-22
---

## Description

After `TASK-10002` (`git.trailer_commits`, split from `TASK-358` on 2026-11-23) and `TASK-572` (`check.unfinished_landed`) land, make `chitty check` warn on `main` about each active ticket whose work is on `main` but which is not `done`. Seen 2026-11-16 (`TASK-318`) and 2026-11-22 (`TASK-540`, `TASK-555`). Split from `TASK-358` on 2026-11-22.

Decisions:

- In `check()` in `src/chitty/check.py`, only when `include_worktree_state` is true and `git.current_branch(repo.root)` equals `repo.config.main_branch`, call `unfinished_landed(git.trailer_commits(repo.root, main_branch), statuses, ticket_directories)` and add one warning per returned ticket, on that ticket's file path: `commit <first 10 characters of SHA> on <main_branch> has work for <ID>, which is <status>`. Warnings do not change the exit code.
- `statuses`: the active (not archived) ticket files `check()` already parsed, by ID. Archived tickets never warn: archiving closes a ticket, and on 2026-11-22 four old archived tickets (`TASK-106`, `TASK-171`, `TASK-231`, `TASK-372`) are archived without being `done` and have code commits. An ID with more than one file, which `check()` already reports as an error, is left out.
- `ticket_directories`: the `directory` of each of `repo.discovered_contexts()`, relative to `repo.root`, including its `archive/` directory (in this repository `chitty/tasks`, `chitty/human`, `chitty/backlog`).
- `include_worktree_state` is false when a write runs the check (`Repo` in `src/chitty/store.py`, where it calls `check(..., include_worktree_state=False)`); that is wanted here too, so writes do not pay for a history scan (about 0.3 s on this repository). Add a comment saying the flag gates both. `check()` is already long, so put the new warnings in a helper called from it.
- Out of scope: commits on other branches; `chitty run` behaviour.

Tests: CLI examples in a new `tests/test_check_unfinished_landed_cli.py`, inheriting `CliTestCase` from `tests/test_cli.py`, real Git on branch `main`. No property: `TASK-358` covers the rule with properties; these check the wiring, a fixed set of cases.

## Acceptance Criteria

- [ ] On `main`, with `TASK-1` `todo` and a commit of `src/x.py` whose message ends `Task: TASK-1`, `chitty check` exits 0 and prints the warning naming `TASK-1` and `todo`; this fails before the change
- [ ] No warning when the only trailer commits are a commit of `TASK-1`'s own ticket file, or a `chitty: ` commit of `src/x.py`; nor for the `src/x.py` commit after `chitty archive TASK-1`; nor after `TASK-1` is moved to `done` (through `review`, with `--override-review-independence` as other CLI tests do); nor in a linked worktree on branch `task-1`
- [ ] `make check` passes

## History

- 2026-11-22T10:00:56Z friendly-jade-stoat → todo
- 2026-11-22T10:01:15Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T10:01:15Z friendly-jade-stoat todo → planning
- 2026-11-22T10:01:26Z friendly-jade-stoat: changed acceptance criteria
- 2026-11-22T10:03:35Z friendly-jade-stoat: changed dependencies, description
- 2026-11-23T18:41:31Z witty-yellow-vole: changed dependencies, description
- 2026-11-26T18:58:14Z zesty-ginger-newt: changed notes
- 2026-11-26T18:58:14Z zesty-ginger-newt planning → to-plan
- 2026-11-26T18:58:32Z zesty-ginger-newt: replaced notes
- 2026-11-26T18:58:32Z zesty-ginger-newt to-plan → planning
- 2026-11-26T18:58:44Z zesty-ginger-newt: changed description
- 2026-11-26T18:58:44Z zesty-ginger-newt planning → cold-read
