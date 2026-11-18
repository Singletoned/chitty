---
title: Rebase the ticket branch onto `main` before review and landing
status: planning
labels:
  - bug
  - needs-minor
priority: high
created: 2026-11-18
---

## Description

Principle (decided 2026-11-18, `docs/plan/ticket-state.md`, on branch `plan/ticket-state` until it lands on `main`): `main` is the base every ticket branch builds on. The runner rebases the branch onto `main` whenever it touches it. Under the one-authoritative-copy model a ticket file changes only on its branch, so ticket files rebase like any other file; there is no ticket merge (`TASK-359` is archived). Any conflict, ticket file or not, goes to an agent.

Today `_prepare_review` merges `main` into the ticket branch with `git.merge_main`, and `_land` merges it again with `git.merge` before fast-forwarding `main` (`src/chitty/run.py`), leaving merge commits on the branch and in `main`.

Decisions:

- New `git.rebase_onto(root: Path, main_branch: str) -> list[str]` in `src/chitty/git.py`: runs `git -c rerere.enabled=false rebase --autostash <main_branch>`; returns `[]` when it completes; on a conflict, leaves the rebase stopped and returns every unmerged path (from `git diff --name-only --diff-filter=U`). Any other Git failure raises `ChittyError`. `TASK-370` reuses it.
- `_prepare_review` calls it instead of `merge_main`. On conflicts it runs `git rebase --abort` and fails the review as `Review failed (integration): rebasing onto <main> conflicts in <paths>` with each path in backticks, as today's merge failure does. `TASK-375` later replaces the abort with a resolution session.
- `_land` calls it instead of `git.merge`, then fast-forwards `main`. A conflict aborts the rebase and is a landing error, as today.
- Remove `git.merge` and `git.merge_main` once nothing uses them.
- Ctrl-C during either rebase aborts it and raises `RunInterrupted` (exit 130): `_prepare_review` adapts its `KeyboardInterrupt` handler, and `_land` gains one. No test: it needs a signal mid-rebase.
- The uncommitted-files block before a review stays.
- In `docs/plan/next-action-and-runner.md`, add the principle paragraph, and say under `## Before a review` and `## Landing` that the branch is rebased onto `main`.

Tests: real-Git, fake-agent runner tests in `tests/test_review_merge.py` and `tests/test_landing.py`, with `git init -b main`; the fake reviewer writes a marker file when it starts. No property: real Git and runner processes over the fixed cases in the criteria; `rebase_onto`'s two outcomes are tested directly in `tests/test_git.py`.

## Notes

On hold 2026-11-18: the ticket state model is being redesigned (the ticket branch is authoritative for its ticket while it exists; no runner writes on `main` for in-flight tickets). See `docs/plan/ticket-state.md` on branch `plan/ticket-state`. Re-plan against that before working.

## History

- 2026-11-18T09:51:20Z witty-ginger-falcon → planning
- 2026-11-18T09:52:34Z witty-ginger-falcon planning → cold-read
- 2026-11-18T09:56:01Z witty-ginger-falcon cold-read → planning
- 2026-11-18T09:56:03Z witty-ginger-falcon: changed description, acceptance criteria
- 2026-11-18T09:56:05Z witty-ginger-falcon planning → todo
- 2026-11-18T15:47:46Z witty-ginger-falcon: changed notes
- 2026-11-18T15:47:46Z witty-ginger-falcon todo → planning
- 2026-11-18T17:57:37Z lively-quartz-crane: changed dependencies, description
- 2026-11-18T17:57:39Z lively-quartz-crane: changed acceptance criteria
