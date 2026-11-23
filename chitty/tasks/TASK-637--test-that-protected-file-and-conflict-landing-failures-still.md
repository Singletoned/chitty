---
title: Test that protected-file and conflict landing failures still end in `error`
status: backlog
depends_on:
  - TASK-609
created: 2026-11-23
---

## Description

Split from TASK-609 (third cold read, 2026-11-23). TASK-609 sends a landing check failure to `doing`; other landing failures must still end in `error`, but the existing tests only check that `_land` raises, so they cannot catch a wrong routing: `test_landing_refuses_protected_change_without_moving_main` (`tests/test_protected_paths.py:96`) and `test_merge_conflict_keeps_main_unchanged_and_worktree_present` (`tests/test_landing.py:181`). No landing-level test covers the post-rebase `_changed_config` check (about `run.py:1282`). Add run-level tests (through `chitty run --mode review`, as in `tests/test_review_merge.py`) asserting `done → error` and a `Runner error (landing)` note for a protected file changed on the branch, a config change, and a conflict that appears because `main` moved during landing.

## History

- 2026-11-23T10:42:57Z witty-russet-gannet → backlog
