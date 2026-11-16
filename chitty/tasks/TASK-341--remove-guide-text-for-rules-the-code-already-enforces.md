---
title: Remove guide text for rules the code already enforces
status: planning
labels:
  - untestable
owner: untestable
created: 2026-11-16
---

## Description

Retro 2026-11-16: the role guides total about 4100 words and reach every repository. These rules are already enforced in code: the verdict-line format and the block after `REVIEW_FAILURE_LIMIT` failed reviews (`src/chitty/store.py`), review independence (`--override-review-independence`), and, in `_prepare_review` in `src/chitty/run.py`, blocking a review whose worktree has uncommitted changes, failing a review on a conflict when merging `main`, and failing a branch that changes the config or the managed `AGENTS.md` block. Shorten each to one line or remove it from `src/chitty/roles/review.md` and `work.md`, relying on the error message, and make sure each error message says what to do.

## History

- 2026-11-16T09:59:49Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:31Z intrepid-coral-raven backlog → planning
- 2026-11-16T10:50:29Z intrepid-coral-raven: changed description
- 2026-11-16T16:48:10Z open-russet-eel: changed labels, owner
