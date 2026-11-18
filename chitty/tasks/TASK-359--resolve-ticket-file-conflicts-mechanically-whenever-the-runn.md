---
title: Resolve ticket-file conflicts mechanically whenever the runner merges `main`
status: planning
created: 2026-11-16
---

## Description

Seen 2026-11-16 on `TASK-333`. `_prepare_review` in `src/chitty/run.py` already merges `main` into the ticket branch before every review, and fails the review as `integration` on a conflict. Here the only conflict was in the ticket file itself: the runner had recorded `error` on `main`, a person moved the ticket back to review there, and the branch still had its older copy. Writing the integration failure from the worktree then hit the stale-copy check (`TASK-333's latest committed version is on branch main`), which stopped the whole `chitty run --loop`. When the merge conflicts only in Chitty ticket files, resolve each one by taking the copy Chitty treats as the latest committed version, commit the merge, and continue with the review. That copy was a strict superset of the branch copy in this case; planning confirms whether that always holds. Conflicts in any other file keep failing the review as `integration` today. Decided 2026-11-18: merging `main` is mechanical and done by the runner; only code conflicts go to an agent. So put the ticket-file resolution in one helper used by every runner merge of `main`: before a review (`_prepare_review`), at landing (`_land`), and before a work session (`TASK-370`), which also uses the same version rule to sync a newer ticket file into the branch after aborting a code conflict.

## History

- 2026-11-16T10:48:09Z intrepid-coral-raven → planning
- 2026-11-16T10:50:28Z intrepid-coral-raven: changed title, description
- 2026-11-18T09:13:54Z witty-ginger-falcon: changed title, description
