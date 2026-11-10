---
title: "Setup guide: validate setup and check in a throwaway worktree; bootstrap targets"
status: review
created: 2026-11-10
---

## Description

Two additions to the setup guide, `src/chitty/roles/setup.md`, from Shelfpath and mullion setups.

- Before declaring the runner ready, run the configured `setup` and `check` commands in a throwaway worktree (`git worktree add --detach`), without `chitty run`, then remove it. This catches reliance on the main checkout's environment, ignored secrets, or local data before a real ticket changes status.
- In a new repository whose first ticket creates the real setup and check targets, commit placeholder targets that only print a message, and have that ticket replace them, so `chitty run` can start it.

Keep each addition to one or two lines. Tests go in a new `tests/test_guide_setup_validation.py` in the style of `tests/test_guide_setup.py`.

## Acceptance Criteria

- [x] `guide("setup")` tells the person to run the configured `setup` and `check` in a throwaway detached worktree before declaring the runner ready, without `chitty run`.
- [x] `guide("setup")` describes committing placeholder setup and check targets when the first ticket creates the real ones.

## Plan

Add focused setup-guide tests asserting both new instructions. Run them first to confirm they fail, then add concise guidance to the setup role. Run format and full checks, verify criteria, commit implementation, and move the ticket to review.

## Notes

Cold read 1 (Haiku): no serious findings. Accepted: placement of each addition is the worker's choice; the throwaway-worktree phrase is the real check for criterion 1. Rejected: specifying failure handling; step 4 already says to fix the reported error before retrying. Possible starting point: `git diff main...refs/cold-read/TASK-241/1`; check it against the current criteria, not trust it.

The new focused guide tests failed before the guide instructions were added, then passed. Full make format and make check passed (425 Python suites and Node tests). The throwaway-worktree validation and placeholder-target guidance are concise additions at the end of setup step 4.

## Summary

Implemented in f6753c0 (Task: TASK-241). Added focused setup-guide coverage; focused tests and full make format/make check pass. No known follow-ups.

## History

- 2026-11-10T14:08:41Z jolly-heron → backlog
- 2026-11-10T14:20:04Z jolly-heron: changed notes
- 2026-11-10T14:20:04Z jolly-heron backlog → todo
- 2026-11-10T17:06:34Z calm-crane todo → doing
- 2026-11-10T17:06:50Z calm-crane: wrote the plan
- 2026-11-10T17:08:56Z calm-crane: changed notes, summary; ticked acceptance criteria
- 2026-11-10T17:08:56Z calm-crane doing → review
