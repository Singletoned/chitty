---
title: Warn in `chitty check` on `main` about active tickets whose work is on `main` but are not done
status: doing
depends_on:
  - TASK-358
  - TASK-572
  - TASK-10002
created: 2026-11-22
---

## Description

`TASK-572` added `check.unfinished_landed` and `TASK-10002` added `git.trailer_commits`. Wire them into `chitty check` so it warns on `main` about each active ticket whose work is on `main` but which is not `done`. Seen 2026-11-16 (`TASK-318`) and 2026-11-22 (`TASK-540`, `TASK-555`).

Change, in `src/chitty/check.py`: a helper called from `check()` (which is already long), only when `include_worktree_state` is true and `git.current_branch(repo.root)` equals `repo.config.main_branch`. It calls `unfinished_landed(git.trailer_commits(repo.root, main_branch), statuses, ticket_directories)` and adds one warning per returned ticket, on that ticket's file: `commit <first 10 characters of SHA> on <main_branch> has work for <ID>, which is <status>`. Warnings do not change the exit code.

- `statuses`: ID to status, from the `tasks` that `check()` already parsed, leaving out archived files (`path.parent.name == ARCHIVE_DIR`) and any ID with more than one path in `by_id` (already reported as an error). Archived tickets never warn: archiving closes a ticket, and some old archived tickets were never `done`.
- `ticket_directories`: each `context.directory` and `context.archive_directory` of `repo.discovered_contexts()`, made relative with `.relative_to(repo.root)` (they are absolute).
- Writes call `check(..., include_worktree_state=False)` in `src/chitty/store.py`, so they skip the history scan (about 0.3 s here). Add a comment that the flag gates both.

Out of scope: commits on other branches; `chitty run`.

Tests: CLI examples in a new `tests/test_check_unfinished_landed_cli.py`, `CliTestCase` from `tests/test_cli.py`, real Git on branch `main`. For the worktree case, `git worktree add -b task-1 <dir>` as `tests/test_cli.py` does, and run the check from that directory (check how `run_cli` takes its working directory). No property: `TASK-572` covers the rule with properties; these check the wiring.

## Acceptance Criteria

- [ ] On `main`, with `TASK-1` `todo` and a commit of `src/x.py` whose message ends `Task: TASK-1`, `chitty check` exits 0 and prints the warning naming `TASK-1` and `todo`; this fails before the change
- [ ] Regression tests, each its own test: no warning when the only trailer commit touches only `TASK-1`'s ticket file; nor for a `chitty: ` commit of `src/x.py`; nor after `chitty archive TASK-1`; nor when `chitty check` runs in a linked worktree on branch `task-1`. `make check` passes

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
- 2026-11-26T19:02:35Z zesty-ginger-newt: changed description, acceptance criteria
- 2026-11-26T19:02:35Z zesty-ginger-newt cold-read → planning
- 2026-11-26T19:02:52Z zesty-ginger-newt planning → todo
- 2026-11-26T23:58:11Z mellow-pearl-badger todo → doing
