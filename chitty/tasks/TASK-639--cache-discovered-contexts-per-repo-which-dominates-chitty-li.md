---
title: Cache `discovered_contexts` per `Repo`, which dominates `chitty list` time
status: cold-read
priority: high
created: 2026-11-23
---

## Description

Decided with the person on 2026-11-22: making `chitty list` faster is a top priority (parent problem: TASK-598). A cold read on 2026-11-23 profiled plain `chitty list` in the `task-598` worktree with cProfile. Of 90 s cumulative, `Repo.discovered_contexts` (`src/chitty/store.py`, about line 306) took 67 s. It is reached through `context_of` (269 calls) and `_dependency_is_done`. Each call walks every ref's ticket file list from `_ref_files()` and runs `ids.parse_filename` on each non-`main` path.

Change, in `Repo` in `src/chitty/store.py`: cache the result of `discovered_contexts()` on the `Repo` object, and clear the cache in `Repo._invalidate`, as is already done for `_ticket_ids`. Return a new list on each call, so a caller that changes it cannot change the cache. Behaviour is otherwise unchanged. A `Repo` lives for one command or MCP call, and Chitty's own writes already call `_invalidate`.

Tests, in a new `tests/test_discovered_contexts_cache.py`. Use a `RepoTestCase` repository made into a Git repository: `git init -b main`, an identity, and one committed ticket from `chitty add`. Use `Repo.open(self.root)`.

- Two calls to `discovered_contexts()` return equal lists. Before the second call, replace the instance's `_ref_files` with a wrapper that counts its calls; the count is 0 after the second call.
- Call `discovered_contexts()` once. Then, after `mkdir chitty/extra`, then a ticket file written by hand into it (copy the committed ticket file to `chitty/extra/EXTRA-1--x.md`), then `repo._invalidate()`, `discovered_contexts()` includes a context named `extra`. In the same sequence without the `_invalidate`, the second call does not include `extra`.
- Changing the returned list (`.clear()`) does not change the next call's result.

Run them against `main` first and record the failure of the first test in a note.

## Acceptance Criteria

- [ ] The three tests in `tests/test_discovered_contexts_cache.py` pass; the first fails against `main`. Record both runs in a note
- [ ] In the ticket worktree, with no ticket commits between runs: `chitty list` prints byte-identical output before the change (code from `git archive "$(git merge-base main HEAD)" src`, extracted into `tmp/before` after `mkdir -p tmp/before`, and run as `PYTHONPATH=tmp/before/src .venv/bin/python -c "from chitty.cli import main; main()" list`) and after it (`.venv/bin/chitty list`). Record the `diff` result and three `time` runs of each in a note
- [ ] `make check` passes

## History

- 2026-11-23T12:07:54Z witty-russet-gannet → planning
- 2026-11-23T12:08:25Z witty-russet-gannet: changed description
- 2026-11-23T12:08:25Z witty-russet-gannet planning → cold-read
