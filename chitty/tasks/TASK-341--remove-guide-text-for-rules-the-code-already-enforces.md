---
title: Remove guide text for rules the code already enforces
status: planning
created: 2026-11-16
---

## Description

Retro 2026-11-16: the role guides total about 4100 words and reach every repository. These rules are already enforced in `src/chitty/store.py`: the verdict-line format (regex check on review transitions), the block after `REVIEW_FAILURE_LIMIT` failed reviews, and review independence (`--override-review-independence`). Shorten each to one line or remove it from `src/chitty/roles/review.md` and `work.md`, relying on the error message, and make sure each error message says what to do.

## History

- 2026-11-16T09:59:49Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:31Z intrepid-coral-raven backlog → planning
