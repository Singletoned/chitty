---
title: Avoid crashing when a branch disappears during historical task discovery
status: backlog
created: 2026-11-09
---

## Description

Observed in Echonomicon on 2026-11-09 at 10:49:59, running `chitty list` with Chitty CLI version `0.1.43`: `git log --topo-order --no-renames --format=%H%x09%ct --name-only refs/heads/main ... refs/heads/task-90 -- chitty` failed with `fatal: bad revision 'refs/heads/task-90'`. A later retry succeeds and `task-90` is absent. Investigation: `src/chitty/git.py:140-154` enumerates mutable ref names with `for-each-ref`, then `_latest_changes` at line 275 passes those names to `git log`, and `_tree_blobs` at line 306 resolves the names again in `git ls-tree`. Concurrent branch cleanup can delete a previously enumerated ref between any of those commands; a moving branch can also make the log and tree snapshots inconsistent. Deterministically reproduced both failures in disposable Git repositories, without touching application branches: create a committed `chitty/example.md`, create branch `task-90`, wrap `_git` to delete that branch immediately after the real `for-each-ref` returns, then call `historical_files(root, Path("chitty"))`. This produces the exact bad-revision error in `_latest_changes`. Repeat deletion immediately after the real `git log` returns instead: `_tree_blobs` fails with `fatal: Not a valid object name refs/heads/task-90`. In both cases an ordinary subsequent `historical_files` call succeeds. Proposed fix: enumerate each ref name and its immutable object ID together, and use that captured object ID consistently for history/tree reads while retaining the captured ref name for display and current-branch preference. Handle specifically demonstrable disappearance races if retries are needed; do not broadly swallow Git errors or return an empty task list on repository corruption. Add deterministic synchronization/hook-based regression tests for deletion after enumeration and after log, plus a moved-ref consistency test; assert remaining task discovery succeeds without a traceback and a consistent snapshot is used. User explicitly reports that branch cleanup must not make `chitty list` blow up.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-09T12:03:06Z eager-puffin → backlog
- 2026-11-09T12:03:08Z eager-puffin: changed notes
