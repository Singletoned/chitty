---
title: Bring a ticket branch up to date when main holds the newer ticket copy
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16 on `TASK-333`. When landing failed, the runner recorded `error` on `main`. A person then moved it back to review with `chitty edit` in the main checkout, which Chitty allowed because `main` held the latest committed copy. The next `chitty run --loop --mode review` stopped the whole loop with `Error: TASK-333's latest committed version is on branch main; run Chitty in worktree <main checkout>`, because the `task-333` branch still had the older copy. Fixed by hand by merging `main` into the branch, which conflicted only in the ticket file, where `main`'s side was a superset. Every ticket repaired by hand after a runner `error` takes this path. Before starting a session, the runner should merge `main` into the ticket branch, as landing already does, so the branch has the newest ticket copy. If that merge conflicts outside the ticket file, record `error` on that ticket and carry on, rather than stopping the loop.

## History

- 2026-11-16T10:48:09Z intrepid-coral-raven → planning
