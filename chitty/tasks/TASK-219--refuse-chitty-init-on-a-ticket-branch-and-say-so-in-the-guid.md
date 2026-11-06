---
title: Refuse `chitty init` on a ticket branch, and say so in the guides
status: done
priority: high
created: 2026-11-06
---

## Description

Ticket branches must never change `chitty.toml` or `AGENTS.md`'s managed block; only `chitty init` on the main checkout may (`TASK-212`, `TASK-218`).

1. **`chitty init` in a linked worktree** (`git.is_linked_worktree`) refuses, with an error naming the main checkout's path. It changes nothing.
   - Move `_main_checkout` from `src/chitty/run.py` to `git.main_checkout`, so `store.py` can use it. `TASK-216` makes the same move, and whichever lands second reuses it.
   - Remove the now-dead "skipping machine-wide Pi setup" linked-worktree branch in `store.py`.
   - `test_worktree_keeps_the_main_checkout_registered` in `tests/test_cli.py` runs `init` in a linked worktree. Change it to expect the refusal.
2. **Guides.** `src/chitty/guide.md` and `src/chitty/roles/work.md` include the sentence "On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`." A test checks for it. Bump `__version__` one patch above `main`'s current version (`scripts/check_version_bump.py` checks it). Don't regenerate this repository's `AGENTS.md`; the main checkout's setup refresh does that after landing.

## Acceptance Criteria

- [x] `chitty init` run in a linked worktree exits non-zero, naming the main checkout, and leaves `chitty.toml` and `AGENTS.md` unchanged.
- [x] `chitty guide work` and the `AGENTS.md` block that `chitty init` writes in a temporary repository both contain that sentence, and `__version__` is bumped.

## Plan

Move main-checkout detection into src/chitty/git.py and make init reject linked worktrees before any writes, including the main checkout path in the error. Remove the obsolete linked-worktree Pi setup branch and update the CLI regression test. Add the required sentence to both guide sources, bump __version__, then run the focused tests and full make format/check.

## Notes

Split from `TASK-212` on 2026-11-06. Items 2 and 3 of its first cold read (`refs/cold-read/TASK-212/1`) implement most of this; that read predates the managed-block sentence.

Verified the linked-worktree regression test fails before the fix and passes after it;  now reports the main checkout and leaves setup files unchanged. Full uv run ruff check --exit-zero .
All checks passed!
uv run ruff format .
296 files left unchanged
uv run python scripts/check_version_bump.py
uv run ruff format --check .
296 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Deleted branch task-1 (was 7de3fd6).
Deleted branch task-1 (was 1d22935).
Deleted branch task-2 (was 77bd714).
npm test

> test
> node --experimental-strip-types --test-reporter=dot --test src/chitty/integrations/pi/tests/chitty.test.ts

....................
...... passes. The guides contain the required sentence and version is 0.1.38.

Reviewed:
1: pass - linked-worktree init refuses, names the main checkout, and preserves setup files.
2: pass - guide sources and generated managed block contain the sentence, and version is bumped; full checks pass.

## Summary

Implemented linked-worktree refusal for `chitty init`, centralized main-checkout detection in `git.main_checkout`, removed the obsolete Pi setup skip, updated guides and regression coverage, and bumped `__version__` to 0.1.38. Verified with the focused regression test and `make format && make check`; ready for review.

## History

- 2026-11-06T18:13:15Z youthful-toad → backlog
- 2026-11-06T18:13:31Z youthful-toad backlog → todo
- 2026-11-06T20:07:51Z honest-falcon todo → doing
- 2026-11-06T20:08:16Z honest-falcon: wrote the plan
- 2026-11-06T20:13:52Z honest-falcon: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:13:52Z honest-falcon doing → review
- 2026-11-06T20:14:10Z honest-falcon: changed summary
- 2026-11-06T20:18:00Z jolly-jay: changed notes; ticked acceptance criteria
- 2026-11-06T20:18:00Z jolly-jay review → done
