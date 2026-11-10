---
title: "Setup guide: validate setup and check in a throwaway worktree; bootstrap targets"
status: backlog
created: 2026-11-10
---

## Description

Two additions to the setup guide, `src/chitty/roles/setup.md`, from Shelfpath and mullion setups.

- Before declaring the runner ready, run the configured `setup` and `check` commands in a throwaway worktree (`git worktree add --detach`), without `chitty run`, then remove it. This catches reliance on the main checkout's environment, ignored secrets, or local data before a real ticket changes status.
- In a new repository whose first ticket creates the real setup and check targets, commit placeholder targets that only print a message, and have that ticket replace them, so `chitty run` can start it.

Keep each addition to one or two lines. Tests go in a new `tests/test_guide_setup_validation.py` in the style of `tests/test_guide_setup.py`.

## Acceptance Criteria

- [ ] `guide("setup")` tells the person to run the configured `setup` and `check` in a throwaway detached worktree before declaring the runner ready, without `chitty run`.
- [ ] `guide("setup")` describes committing placeholder setup and check targets when the first ticket creates the real ones.

## History

- 2026-11-10T14:08:41Z jolly-heron → backlog
