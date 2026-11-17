---
title: Resolve ticket-file conflicts when merging main before a review
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16 on `TASK-333`. `_prepare_review` in `src/chitty/run.py` already merges `main` into the ticket branch before every review, and fails the review as `integration` on a conflict. Here the only conflict was in the ticket file itself: the runner had recorded `error` on `main`, a person moved the ticket back to review there, and the branch still had its older copy. Writing the integration failure from the worktree then hit the stale-copy check (`TASK-333's latest committed version is on branch main`), which stopped the whole `chitty run --loop`. When the merge conflicts only in Chitty ticket files, resolve each one by taking the copy Chitty treats as the latest committed version, commit the merge, and continue with the review. That copy was a strict superset of the branch copy in this case; planning confirms whether that always holds. Conflicts in any other file keep failing the review as `integration` today.

## History

- 2026-11-16T10:48:09Z intrepid-coral-raven → planning
- 2026-11-16T10:50:28Z intrepid-coral-raven: changed title, description
