---
title: Close from `main` a ticket whose work already landed or is superseded
status: backlog
depends_on:
  - TASK-599
created: 2026-11-26
---

## Description

From TASK-681 (echonomicon, 2026-11-23): TASK-160 and TASK-164 sat in `planning` though their work had already landed on `main` (`022f1db`, `0426d87`). Closing them was awkward. `chitty edit -s done` from `planning` is refused ("setting status done requires -s review first"), and `review` would make a reviewer fail criteria that need the code to fail first. `chitty archive` on `main` is refused while the latest version is on the ticket branch. Archiving in the ticket worktree only commits on that branch, so `main` then needs a rebase and fast-forward, and it fails if the branch also holds superseded code.

Asked for: a supported "close as already done or superseded" path from `planning`, run from `main`, that records the reason and retires or flags the ticket branch. From TASK-662 (shelfpath): there is no way to cancel from `main` a ticket whose latest version is on its ticket branch, short of deleting that branch by hand.

Likely built on the `dropped` status (TASK-599) and the checkout-local edits of TASK-602.

## History

- 2026-11-26T11:38:16Z brisk-bronze-adder → backlog
