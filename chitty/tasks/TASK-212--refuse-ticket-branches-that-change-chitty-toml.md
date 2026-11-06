---
title: Refuse ticket branches that change `chitty.toml`
status: backlog
priority: high
created: 2026-11-06
---

## Description

Only `chitty init` in the main checkout may change a repository's Chitty config. In other repositories it is vital that ticket branches never do. On 2026-11-06, `task-173`, `task-179` and `task-181` each changed `chitty_version` in `chitty.toml`, through `chitty init` or an automatic setup upgrade run on the branch. `main`'s `chitty` then refused to write to the newer ones (`repository needs Chitty 0.1.35 or later`), and the review loop stopped. `TASK-204` already stops automatic upgrades in linked worktrees. Make the rule a hard check:

1. **Before review.** In `_prepare_review` in `src/chitty/run.py`, after the rebase onto `main`, fail the ticket if the branch changes the Chitty config compared with `main`. Use the existing `_fail_review`, with `Review failed (work): the branch changes `chitty.toml`; only `chitty init` on the main checkout may change it. Restore it with `git checkout main -- chitty.toml`.`
   - Use `git diff --quiet main...HEAD -- chitty.toml`.
   - When the config is in `pyproject.toml` (`config_source` in `src/chitty/config.py`), compare the parsed `[tool.chitty]` table on both sides instead, because a branch may legitimately change other parts of `pyproject.toml`.
   - `TASK-131` must repeat this check when it lands a ticket.
2. **`chitty init` in a linked worktree** (`git.is_linked_worktree`) refuses, with an error naming the main checkout's path. It changes nothing.
3. **Guides.** `src/chitty/guide.md` and `src/chitty/roles/work.md` say never to edit `chitty.toml` or run `chitty init` on a ticket branch. That changes the managed block, so bump `__version__` at patch level.

Out of scope: `AGENTS.md`'s managed block, which a branch changing the guide text legitimately regenerates in this repository.

## Acceptance Criteria

- [ ] A test runs `chitty run --mode review` on a branch that changes `chitty.toml` and asserts the ticket moves to `doing` with that note and no agent runs. Another, with the config in `[tool.chitty]`, shows that a change elsewhere in `pyproject.toml` passes and a change to `[tool.chitty]` fails.
- [ ] `chitty init` run in a linked worktree exits non-zero naming the main checkout, and leaves `chitty.toml` and `AGENTS.md` unchanged.
- [ ] `chitty guide work` and the `AGENTS.md` block that `chitty init` writes both say not to edit `chitty.toml` or run `chitty init` on a ticket branch, and `__version__` is bumped.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-212/1`; the test failed before and passed after; `make check` OK, 330 tests). Outcomes:
- Newer branches with unknown or changed keys: fixed, the ticket now says top-level keys already load with a warning and should be tested. Nested or changed keys are out of scope (`TASK-201`).
- Existing coverage of the main-checkout refusal: fixed, the ticket names `test_newer_setup_blocks_writes`.
- Version bump: fixed, the ticket says none.
- Using `99.0.0` rather than the real version: accepted, the ticket gives it as an example.
- `PLAN.md` sentences moved together: accepted.

Rescoped on 2026-11-06. The human said branches must never update `chitty.toml` (only `chitty init` may) and asked for a hard check before merging. The old scope, letting `main`'s `chitty` write on a branch recording a newer version, isn't needed once branches can't change the version. The three affected branches were restored to `main`'s `chitty.toml` by hand, and the stale cold-read ref `refs/cold-read/TASK-212/1` was deleted.

## History

- 2026-11-06T16:15:42Z youthful-toad → backlog
- 2026-11-06T16:22:42Z youthful-toad: changed description, notes
- 2026-11-06T16:22:42Z youthful-toad backlog → todo
- 2026-11-06T16:44:06Z youthful-toad: changed title, description, acceptance criteria, notes
- 2026-11-06T16:44:06Z youthful-toad todo → backlog
