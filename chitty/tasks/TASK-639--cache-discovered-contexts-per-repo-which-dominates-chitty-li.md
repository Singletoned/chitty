---
title: Cache `discovered_contexts` per `Repo`, which dominates `chitty list` time
status: doing
priority: high
created: 2026-11-23
---

## Description

Decided with the person on 2026-11-22: making `chitty list` faster is a top priority (parent problem: TASK-598). A cold read on 2026-11-23 profiled plain `chitty list` in the `task-598` worktree with cProfile. Of 90 s cumulative, `Repo.discovered_contexts` (`src/chitty/store.py`, about line 306) took 67 s. It is reached through `context_of` (269 calls) and `_dependency_is_done`. Each call walks every ref's ticket file list from `_ref_files()` and runs `ids.parse_filename` on each non-`main` path.

Change, in `Repo` in `src/chitty/store.py`: cache the result of `discovered_contexts()` on the `Repo` object, and clear the cache in `Repo._invalidate`, as is already done for `_ticket_ids`. Return a new list on each call, so a caller that changes it cannot change the cache. Behaviour is otherwise unchanged. A `Repo` lives for one command or MCP call, and Chitty's own writes already call `_invalidate`. Check every `Repo` method that creates or removes a directory under `chitty/` (for example those that `mkdir` an archive or context directory) and calls `discovered_contexts` afterwards on the same object; make sure `_invalidate` runs between the two, and list the methods you checked in a note.

Tests, in a new `tests/test_discovered_contexts_cache.py`. Use a `RepoTestCase` repository made into a Git repository: `git init -b main`, an identity, and one committed ticket from `chitty add`. Use `Repo.open(self.root)`.

- Two calls to `discovered_contexts()` return equal lists. After the first call, replace the instance's `_ref_files` with a wrapper that counts its calls; read the count after the second call: it is 0.
- Use two `Repo.open(self.root)` instances, A and B, each calling `discovered_contexts()` once before the directory exists. Then, after `mkdir chitty/extra`, then a ticket file written by hand into it (copy the committed ticket file to `chitty/extra/EXTRA-1--x.md`), then A calls `_invalidate()` and its next `discovered_contexts()` includes a context named `extra`; B does not call `_invalidate()` and its next call does not include `extra`.
- Changing the returned list (`.clear()`) does not change the next call's result. This guard already passes on `main`.

Run them against `main` first and record the failure of the first test in a note.

## Acceptance Criteria

- [ ] The three tests in `tests/test_discovered_contexts_cache.py` pass; the first fails against `main`. Record both runs in a note
- [ ] In the ticket worktree, with `cwd` at the worktree root for both runs and no ticket commits between them: `chitty list` prints byte-identical output before the change (code from `git archive "$(git merge-base main HEAD)" src`, extracted into `tmp/before` after `mkdir -p tmp/before`, and run as `PYTHONPATH=tmp/before/src .venv/bin/python -c "from chitty.cli import main; main()" list`) and after it (`.venv/bin/chitty list`). Record the `diff` result and three `time` runs of each in a note
- [ ] `make check` passes

## Plan

Add focused cache tests and verify the regression on the baseline; cache discovered contexts per Repo with invalidation, inspect directory mutations, and run output, timing and project checks.

## Notes

Planner, 2026-11-23: a cold read found nothing serious. Clarified the test setups (when the wrapper is installed, two `Repo` objects for the invalidation case, and that the copy guard passes on `main`), the `cwd` for the comparison, and a check that directory-changing writes invalidate. `tmp/before` needs no ruff exclusion: `tmp/` is gitignored, and ruff skips gitignored files.

Baseline tests on unchanged main code: `pytest -q tests/test_discovered_contexts_cache.py` gave 2 failures (cache call count 1; stale instance observed extra) and 1 pass (copy guard). After fix: 3 passed. Checked directory mutations: `Repo._set_archived` invalidates after mkdir and rename; `Repo._write` invalidates after mkdir and write. Other mkdir/rmdir occurrences are module-level initialization or rollback, not Repo methods.

Comparison: three baseline real times 9.086, 8.744, 8.868 seconds; three changed real times 4.793, 4.922, 4.964 seconds. Initial diff reflected concurrent TASK-626 status change; rerunning both commands without intervening ticket commits gave empty diff. `make check` passed (1175 tests, 819 subtests).

## History

- 2026-11-23T12:07:54Z witty-russet-gannet → planning
- 2026-11-23T12:08:25Z witty-russet-gannet: changed description
- 2026-11-23T12:08:25Z witty-russet-gannet planning → cold-read
- 2026-11-23T12:10:21Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:10:21Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:25:07Z golden-ochre-yellowhammer todo → doing
- 2026-11-23T12:27:22Z golden-ochre-yellowhammer: wrote the plan
- 2026-11-23T12:31:17Z golden-ochre-yellowhammer: changed notes
