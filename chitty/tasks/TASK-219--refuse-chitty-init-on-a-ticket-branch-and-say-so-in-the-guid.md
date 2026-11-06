---
title: Refuse `chitty init` on a ticket branch, and say so in the guides
status: doing
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

- [ ] `chitty init` run in a linked worktree exits non-zero, naming the main checkout, and leaves `chitty.toml` and `AGENTS.md` unchanged.
- [ ] `chitty guide work` and the `AGENTS.md` block that `chitty init` writes in a temporary repository both contain that sentence, and `__version__` is bumped.

## Notes

Split from `TASK-212` on 2026-11-06. Items 2 and 3 of its first cold read (`refs/cold-read/TASK-212/1`) implement most of this; that read predates the managed-block sentence.

## History

- 2026-11-06T18:13:15Z youthful-toad → backlog
- 2026-11-06T18:13:31Z youthful-toad backlog → todo
- 2026-11-06T20:07:51Z honest-falcon todo → doing
