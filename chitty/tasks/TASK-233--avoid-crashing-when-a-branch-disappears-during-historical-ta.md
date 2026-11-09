---
title: Avoid crashing when a branch disappears during historical task discovery
status: backlog
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-09
---

## Description

Observed in Echonomicon on 2026-11-09 at 10:49:59, running `chitty list` with Chitty CLI version `0.1.43`: `git log --topo-order --no-renames --format=%H%x09%ct --name-only refs/heads/main ... refs/heads/task-90 -- chitty` failed with `fatal: bad revision 'refs/heads/task-90'`. A later retry succeeds and `task-90` is absent. Investigation: `src/chitty/git.py:140-154` enumerates mutable ref names with `for-each-ref`, then `_latest_changes` at line 275 passes those names to `git log`, and `_tree_blobs` at line 306 resolves the names again in `git ls-tree`. Concurrent branch cleanup can delete a previously enumerated ref between any of those commands; a moving branch can also make the log and tree snapshots inconsistent. Deterministically reproduced both failures in disposable Git repositories, without touching application branches: create a committed `chitty/example.md`, create branch `task-90`, wrap `_git` to delete that branch immediately after the real `for-each-ref` returns, then call `historical_files(root, Path("chitty"))`. This produces the exact bad-revision error in `_latest_changes`. Repeat deletion immediately after the real `git log` returns instead: `_tree_blobs` fails with `fatal: Not a valid object name refs/heads/task-90`. In both cases an ordinary subsequent `historical_files` call succeeds. Proposed fix: enumerate each ref name and its immutable object ID together, and use that captured object ID consistently for history/tree reads while retaining the captured ref name for display and current-branch preference. Handle specifically demonstrable disappearance races if retries are needed; do not broadly swallow Git errors or return an empty task list on repository corruption. Add deterministic synchronization/hook-based regression tests for deletion after enumeration and after log, plus a moved-ref consistency test; assert remaining task discovery succeeds without a traceback and a consistent snapshot is used. User explicitly reports that branch cleanup must not make `chitty list` blow up.

## Acceptance Criteria

- [ ] Deterministic real-Git regression tests delete a ticket branch after ref enumeration and after `git log`, fail against the old behavior, and show `historical_files` uses one captured ref snapshot rather than raising a bad-revision error; the next call reflects the deleted branch.
- [ ] A test moves a ref between enumeration and tree reading and shows history and blobs use the same captured commit; unrelated Git failures still raise errors rather than being swallowed. `make check` passes.

## Notes

Suggestion origin: echonomicon

Triage: distinct from completed TASK-164, which deliberately surfaced Git errors instead of silently discarding tickets. This suggestion addresses only concurrent ref deletion/movement by using the ref object IDs captured at enumeration, without relaxing failures for repository corruption. Keep the imported reproduction in the description; backlog until implementing cold read.

Clarification: one call uses the refs captured at its start, including a branch deleted during the call; the next call may omit it. This matches the proposed immutable-object-ID fix and avoids a contradictory requirement to both preserve the snapshot and immediately drop the branch. The tests should fail against the original mutable-name implementation.

## History

- 2026-11-09T12:03:06Z eager-puffin → backlog
- 2026-11-09T12:03:08Z eager-puffin: changed notes
- 2026-11-09T12:04:53Z eager-puffin: changed labels, priority, parent, acceptance criteria, notes
- 2026-11-09T12:07:50Z eager-puffin: changed acceptance criteria, notes
