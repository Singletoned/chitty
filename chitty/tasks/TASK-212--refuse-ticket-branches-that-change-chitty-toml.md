---
title: Refuse ticket branches that change `chitty.toml`
status: doing
priority: high
created: 2026-11-06
---

## Description

Only `chitty init` in the main checkout may change a repository's Chitty config. In other repositories it is vital that ticket branches never do. On 2026-11-06, `task-173`, `task-179` and `task-181` each changed `chitty_version` in `chitty.toml`, through `chitty init` or an automatic setup upgrade run on the branch. `main`'s `chitty` then refused to write to the newer ones (`repository needs Chitty 0.1.35 or later`), and the review loop stopped. `TASK-204` already stops automatic upgrades in linked worktrees. This ticket is the check before review. `TASK-218` adds the same check for `AGENTS.md`'s managed block, and `TASK-219` covers `chitty init` and the guides.

**Before review.** In `_prepare_review` in `src/chitty/run.py`, after the rebase onto `main`, fail the ticket if the branch changes the Chitty config compared with `main`. Use the existing `_fail_review`, with `Review failed (work): the branch changes `<file>`; only `chitty init` on the main checkout may change it. Restore it with `git checkout main -- <file>`.`, where `<file>` is `chitty.toml` or `pyproject.toml`, whichever holds the config
   - Use `git diff --quiet main...HEAD -- chitty.toml`.
   - When the config is in `pyproject.toml` (`config_source` in `src/chitty/config.py`), compare the parsed `[tool.chitty]` table on both sides instead, because a branch may legitimately change other parts of `pyproject.toml`.
   - `TASK-131` must repeat this check when it lands a ticket.
- `test_run_reviews_branch_with_newer_config_key` in `tests/test_next.py` expects a branch that changes `chitty.toml` to pass review. Delete it: under this rule, that branch fails.
- The check sees only branches that rebase cleanly. A branch whose rebase conflicts in the config already fails as `integration`.
- A config file present on only one side counts as a change.
- `chitty run` refreshes the main checkout's setup before the rebase, so a test fixture must use the config `chitty init` would write, or the rebase conflicts for the wrong reason. Assert the exact `Review failed (work)` note, not only the `doing` status.

No `__version__` bump: nothing `chitty init` writes changes.

## Acceptance Criteria

- [ ] A test runs `chitty run --mode review` on a branch that changes `chitty.toml` and asserts the ticket moves to `doing` with that note and no agent runs. Another, with the config in `[tool.chitty]`, shows that a change elsewhere in `pyproject.toml` passes and a change to `[tool.chitty]` fails.

## Plan

Add a review preflight check after a clean rebase that compares the branch's Chitty configuration with main, using a parsed [tool.chitty] table for pyproject.toml and a file diff for chitty.toml. Fail through the existing review path with the specified note and add regression coverage for both config sources, including a pyproject-only unrelated change passing. Remove the obsolete newer-config-key expectation. Run the targeted tests and make check.

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

Correction to the previous note: `TASK-144` has already landed, so no open branch is affected.

Split on 2026-11-06 after the item-4 cold read (Sonnet, `refs/cold-read/TASK-212/2`, `make check` OK) found it too big. This ticket keeps item 1; the managed block is `TASK-218`; `init` and the guides are `TASK-219`. Read outcomes that apply here:
- The test-fixture trap: fixed, the ticket now says to use the config `init` writes and to assert the exact note.
- Rebase conflicts in the config: stated, they fail as `integration` first.
- A file on only one side: decided, it counts as a change.
Also, the earlier note saying no open branch is affected is wrong: `task-179` and `task-181` change `AGENTS.md`'s block, which `TASK-218` will catch.

## History

- 2026-11-06T16:15:42Z youthful-toad → backlog
- 2026-11-06T16:22:42Z youthful-toad: changed description, notes
- 2026-11-06T16:22:42Z youthful-toad backlog → todo
- 2026-11-06T16:44:06Z youthful-toad: changed title, description, acceptance criteria, notes
- 2026-11-06T16:44:06Z youthful-toad todo → backlog
- 2026-11-06T17:09:40Z youthful-toad: changed description, notes
- 2026-11-06T17:09:40Z youthful-toad backlog → todo
- 2026-11-06T17:48:05Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T17:48:19Z youthful-toad: changed notes
- 2026-11-06T18:13:05Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T18:51:35Z lively-kestrel todo → doing
- 2026-11-06T18:51:57Z lively-kestrel: wrote the plan
