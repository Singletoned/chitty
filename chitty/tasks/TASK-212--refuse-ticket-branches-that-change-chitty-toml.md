---
title: Refuse ticket branches that change `chitty.toml`
status: todo
priority: high
created: 2026-11-06
---

## Description

Only `chitty init` in the main checkout may change a repository's Chitty config. In other repositories it is vital that ticket branches never do. On 2026-11-06, `task-173`, `task-179` and `task-181` each changed `chitty_version` in `chitty.toml`, through `chitty init` or an automatic setup upgrade run on the branch. `main`'s `chitty` then refused to write to the newer ones (`repository needs Chitty 0.1.35 or later`), and the review loop stopped. `TASK-204` already stops automatic upgrades in linked worktrees. Make the rule a hard check:

1. **Before review.** In `_prepare_review` in `src/chitty/run.py`, after the rebase onto `main`, fail the ticket if the branch changes the Chitty config compared with `main`. Use the existing `_fail_review`, with `Review failed (work): the branch changes `<file>`; only `chitty init` on the main checkout may change it. Restore it with `git checkout main -- <file>`.`, where `<file>` is `chitty.toml` or `pyproject.toml`, whichever holds the config
   - Use `git diff --quiet main...HEAD -- chitty.toml`.
   - When the config is in `pyproject.toml` (`config_source` in `src/chitty/config.py`), compare the parsed `[tool.chitty]` table on both sides instead, because a branch may legitimately change other parts of `pyproject.toml`.
   - `TASK-131` must repeat this check when it lands a ticket.
2. **`chitty init` in a linked worktree** (`git.is_linked_worktree`) refuses, with an error naming the main checkout's path. It changes nothing. Move `_main_checkout` from `src/chitty/run.py` to `git.main_checkout` so `store.py` can use it. Remove the now-dead "skipping machine-wide Pi setup" linked-worktree branch in `store.py`.
   - `test_worktree_keeps_the_main_checkout_registered` in `tests/test_cli.py` runs `init` in a linked worktree. Change it to expect the refusal.
   - `test_run_reviews_branch_with_newer_config_key` in `tests/test_next.py` expects a branch that changes `chitty.toml` to pass review. Delete it: under this rule, that branch fails.
3. **Guides.** `src/chitty/guide.md` and `src/chitty/roles/work.md` say never to edit `chitty.toml` or run `chitty init` on a ticket branch. Use the phrase "On a ticket branch, never edit `chitty.toml` or run `chitty init`", so a test can check for it. That changes the managed block, so bump `__version__` one patch above `main`'s current version (`scripts/check_version_bump.py` checks it). The main checkout's setup refresh regenerates this repository's `AGENTS.md` after landing.

4. **`AGENTS.md`'s managed block** gets the same rule (the human's decision, 2026-11-06). Only `chitty init` on the main checkout writes it. In the same `_prepare_review` check, fail the ticket if the branch changes the managed block of `AGENTS.md` compared with `main`, with `Review failed (work): the branch changes Chitty's managed block in `AGENTS.md`; only `chitty init` on the main checkout may change it. Restore that block from `main`.``
   - The block is the text from the `GUIDE_BEGIN` line to the `GUIDE_END` line in `src/chitty/store.py`. A file without markers uses the legacy `## Chitty` section, as `_managed_agents` finds it. Factor that lookup out of `_managed_agents`, so both use one function.
   - Edits to the rest of `AGENTS.md` are allowed.
   - In this repository, a branch that changes `src/chitty/guide.md` leaves `AGENTS.md` alone; the main checkout's setup refresh regenerates it after landing.

## Acceptance Criteria

- [ ] A test runs `chitty run --mode review` on a branch that changes `chitty.toml` and asserts the ticket moves to `doing` with that note and no agent runs. Another, with the config in `[tool.chitty]`, shows that a change elsewhere in `pyproject.toml` passes and a change to `[tool.chitty]` fails.
- [ ] `chitty init` run in a linked worktree exits non-zero naming the main checkout, and leaves `chitty.toml` and `AGENTS.md` unchanged.
- [ ] `chitty guide work` and the `AGENTS.md` block that `chitty init` writes both say not to edit `chitty.toml` or run `chitty init` on a ticket branch, and `__version__` is bumped.
- [ ] A test shows a branch that changes text inside `AGENTS.md`'s managed block failing review with that note, and one that changes only text outside the block passing.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-212/1`; the test failed before and passed after; `make check` OK, 330 tests). Outcomes:
- Newer branches with unknown or changed keys: fixed, the ticket now says top-level keys already load with a warning and should be tested. Nested or changed keys are out of scope (`TASK-201`).
- Existing coverage of the main-checkout refusal: fixed, the ticket names `test_newer_setup_blocks_writes`.
- Version bump: fixed, the ticket says none.
- Using `99.0.0` rather than the real version: accepted, the ticket gives it as an example.
- `PLAN.md` sentences moved together: accepted.

Rescoped on 2026-11-06. The human said branches must never update `chitty.toml` (only `chitty init` may) and asked for a hard check before merging. The old scope, letting `main`'s `chitty` write on a branch recording a newer version, isn't needed once branches can't change the version. The three affected branches were restored to `main`'s `chitty.toml` by hand, and the stale cold-read ref `refs/cold-read/TASK-212/1` was deleted.

Cold read 1 of the rescoped ticket (Sonnet, `refs/cold-read/TASK-212/1`; the tests failed before and passed after; `make check` OK). Outcomes:
- Two existing tests contradict the rule: fixed, the ticket names them. One changes to expect the refusal; the other is deleted, by decision.
- Version number: fixed, one patch above `main`'s at the time.
- Criterion 3 had no defined phrase: fixed, the ticket gives one.
- The note always said `chitty.toml`: fixed, it names whichever file holds the config.
- Dead Pi-setup branch: fixed, remove it.
- `_main_checkout` moves to `git.py`: accepted.
- `main...HEAD` after the rebase: confirmed correct, including when `main` itself changed the config.
- `AGENTS.md` stays stale until the main checkout refreshes it: stated.
- The `TASK-131` check: follow-up, already noted there.
The reader's ref predates these fixes (fixed note text, kept the dead code), so check it against the ticket rather than copying it.

Extended on 2026-11-06. The human agreed that branches must not regenerate `AGENTS.md`'s managed block either, so the check now covers it (item 4 and criterion 4). The cold-read ref predates this. Also: `task-144` changed the block's markers on its branch, so if it's still open when this lands, its review will fail until the block is restored.

## History

- 2026-11-06T16:15:42Z youthful-toad → backlog
- 2026-11-06T16:22:42Z youthful-toad: changed description, notes
- 2026-11-06T16:22:42Z youthful-toad backlog → todo
- 2026-11-06T16:44:06Z youthful-toad: changed title, description, acceptance criteria, notes
- 2026-11-06T16:44:06Z youthful-toad todo → backlog
- 2026-11-06T17:09:40Z youthful-toad: changed description, notes
- 2026-11-06T17:09:40Z youthful-toad backlog → todo
- 2026-11-06T17:48:05Z youthful-toad: changed description, acceptance criteria, notes
