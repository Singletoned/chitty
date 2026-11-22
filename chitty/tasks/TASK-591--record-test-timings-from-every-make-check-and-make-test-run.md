---
title: Record test timings from every `make check` and `make test` run
status: planning
owner: plucky-umber-wren
depends_on:
  - TASK-590
  - TASK-589
created: 2026-11-22
---

## Description

`TASK-590` adds `tests.timing.TimingResult`, a `unittest-parallel` result class that appends one JSON line per test to `TEST_TIMINGS_FILE`, and needs `TEST_TIER` and `TEST_COMMIT` when that is set. This ticket turns it on for the two `Makefile` test runs, so every run by every agent and worktree adds to one history.

`Makefile`, on the `unittest-parallel` line of both `check` and `test`: add `TEST_TIMINGS_FILE="$$(git rev-parse --path-format=absolute --git-common-dir)/chitty/test-timings.jsonl"` and `TEST_COMMIT="$$(git rev-parse HEAD)"` to its environment and `--result tests.timing.TimingResult` to its options. Keep what is already on each line (`TEST_TIER`, and the coverage options `TASK-589` adds to `test`); read the lines from the `Makefile` when you start. The git common directory is shared by every worktree, so all runs land in one file in the main checkout's `.git`, outside any working tree (no `.gitignore` change). `scripts/check_linux.sh` makes its own repository in the container before `make check`, so this works there and those records are discarded with the container.

One line in `AGENTS.md`, in the bullet about `make check` and `make test`: both append per-test timings and outcomes to `.git/chitty/test-timings.jsonl` in the main checkout.

Out of scope: summarising the file and the retro step (a later ticket).

No property or unit test: build configuration, checked by the commands in the criteria; `TASK-590` tests the recorder itself.

## Acceptance Criteria

- [ ] `make -n check` and `make -n test` each show `--result tests.timing.TimingResult`, `TEST_TIMINGS_FILE=` ending `/chitty/test-timings.jsonl` and `TEST_COMMIT=` on their `unittest-parallel` line, with the options already there kept
- [ ] In a worktree, count the lines of `$(git rev-parse --path-format=absolute --git-common-dir)/chitty/test-timings.jsonl` (0 if absent), run `make check`, and count again: the file gained exactly the `Ran N tests` count (the suite has no class or module fixture errors); every new line has `tier` `check` and `commit` equal to `git rev-parse HEAD`; `git status --short` is empty; and `make check` passed. Record the counts in a note

## Notes

Planner, 2026-11-22: split from `TASK-590` after its third cold read. Relies on what `TASK-590` builds; keep in `planning` until it is `done`, then compare and cold-read before `todo`.

## History

- 2026-11-22T17:15:30Z plucky-umber-wren → planning
