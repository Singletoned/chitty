---
title: Reviews land on `main` by fast-forward only
status: todo
priority: high
created: 2026-11-06
---

## Description

A passed review must land on `main` as a fast-forward, never as a merge commit. Being fast-forwardable is part of passing.

`chitty run --mode review` already rebases the branch onto `main` before the reviewer starts (`_prepare_review` in `src/chitty/run.py`). But `main` can move while the review runs, and the guides only say "merge its branch into `main`", so reviewers make `--no-ff` merges.

Change the guidance so that a reviewer passing a ticket:

1. Rebases the branch onto `main` in the ticket's worktree with `git rebase main`. Do not merge `main` into the branch: the merge commit would then land on `main` and history would no longer be linear. If there's a conflict the reviewer can't resolve without changing the work, fail the review with cause `integration`.
2. Runs the repository's check again in the worktree. If it fails, fail the review with cause `integration` and `--uncheck` the criteria it breaks.
3. Sets `-s done --note "Reviewed: ..."` on the branch. This commit must be on the branch so that it lands with the work.
4. From the main checkout, runs `git merge --ff-only <branch>`. If that refuses because `main` moved again, go back to step 1. The `done` commit is rebased along with the rest.

Files:
- `src/chitty/roles/review.md`, the "On a pass" bullet.
- `src/chitty/guide.md`, the "On a pass, merge the branch into `main`" sentence. This is the managed block that `chitty init` writes into `AGENTS.md`. Re-run `chitty init` here so this repo's `AGENTS.md` picks it up.
- `PLAN.md`:
  - In "Pipeline and feedback", add the rule and why. Fast-forward keeps history linear, and the commits that were reviewed are the ones that land.
  - Fix the "Agent instructions" bullet that says the reviewer merges into `main`.
  - Keep the reference to `TASK-131`: that ticket will automate landing, and it should land by fast-forward too.
- `src/chitty/__init__.py`: bump `__version__` at patch level, because the managed guide block changes. The rule is in `AGENTS.md`, which `CLAUDE.md` links to.

Out of scope:
- Making `chitty run` do the merge itself (`TASK-131`), or check that a merge was a fast-forward.
- Setting `merge.ff` in any Git config.

## Acceptance Criteria

- [ ] `src/chitty/roles/review.md` and `src/chitty/guide.md` tell a reviewer to `git rebase main`, re-run the check, set `done` on the branch, then `git merge --ff-only`, and to repeat if `main` moved. A test in `tests/` asserts that `chitty guide review` and the `AGENTS.md` block that `chitty init` writes both contain `--ff-only` and `git rebase main`.
- [ ] `PLAN.md`'s "Pipeline and feedback" section records the fast-forward-only rule and why, still references `TASK-131`, and the "Agent instructions" bullet no longer says to merge. `grep -rn 'no-ff' src PLAN.md AGENTS.md` finds nothing.
- [ ] `__version__` in `src/chitty/__init__.py` is bumped at patch level, and re-running `chitty init` leaves no diff in `AGENTS.md` or `chitty.toml`.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-203/1`; test failed before and passed after; `make check` OK). Outcomes:
- Allowing `git merge main` contradicted linear history: fixed, the ticket now requires rebase only.
- Order of `done` and the merge: fixed. `done` goes on the branch after the re-check and before `--ff-only`, and rides along on a re-rebase.
- What happens when the re-check fails: fixed, fail with `integration` and uncheck the broken criteria.
- "Review section of `PLAN.md`" was ambiguous: fixed, it now names "Pipeline and feedback" and the "Agent instructions" bullet. The reader removed the `TASK-131` reference; the ticket now says keep it, because `TASK-131` is the future automated landing.
- Criterion 3 couldn't be checked mechanically: fixed, it now says re-running `chitty init` leaves no diff.
- "See `AGENTS.md`": rejected, `CLAUDE.md` is a symlink to `AGENTS.md`, so it's the same file. The ticket now says so.
- `make check` takes about 4 minutes under load: noted for the worker, no change.

## History

- 2026-11-06T11:27:28Z youthful-toad → backlog
- 2026-11-06T11:33:45Z youthful-toad: changed description, notes
- 2026-11-06T11:33:57Z youthful-toad: changed acceptance criteria
- 2026-11-06T11:33:57Z youthful-toad backlog → todo
