---
title: Check saved worktree work round-trips with a property
status: planning
depends_on:
  - TASK-534
parent: TASK-370
created: 2026-11-22
---

## Description

Split from `TASK-524` on 2026-11-21. After `TASK-524` and `TASK-534`, `git.save_work` and `git.restore_work` save and restore uncommitted work under `refs/chitty/stash/<ID>`. This ticket adds a generated round-trip property. Draft: keep in planning until `TASK-534` lands.

Property `test_save_then_restore_round_trips` in `tests/test_git_saved_work.py`, Hypothesis with `@settings(max_examples=25, deadline=None)`, as in `tests/test_git.py`: draw 1 to 6 files committed on `main`, and, independently for each, one change: unchanged, edited and left unstaged, edited and staged, edited, staged and edited again, or deleted; then 0 to 3 new untracked files and 0 to 2 ignored files (listed in a committed `.gitignore`), with random printable contents. An example whose only change is to ignored files is redrawn with `assume`. Names come from a fixed pool of flat names; untracked names never match `.gitignore`, and ignored names are disjoint from the others. First, on the clean tree, make an unrelated edit and `git stash push` it; record `git stash list`. Then make the drawn changes and record every non-ignored file's bytes (or absence) and every ignored file's bytes. After `save_work(root, "refs/chitty/stash/TASK-1", "m")`: `True`, `git status --porcelain` empty, the ref exists, ignored files unchanged. Then, at random, commit a new `main-only.txt` (never a drawn name). After `restore_work`: `True`, every recorded file has its recorded bytes or absence, ignored files unchanged, the ref gone, and `git stash list` equals the recorded list.

## Acceptance Criteria

- [ ] The round-trip property passes, and fails against a `restore_work` that skips `git update-ref -d` (the ref-gone assertion) and against a `save_work` that omits `git add -A` (untracked files lost); a note records both runs; `make check` passes

## History

- 2026-11-22T00:06:31Z lively-zinc-newt → planning
