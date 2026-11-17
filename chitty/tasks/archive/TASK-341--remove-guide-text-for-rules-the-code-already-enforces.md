---
title: Remove guide text for rules the code already enforces
status: done
labels:
  - untestable
owner: untestable
created: 2026-11-16
---

## Description

Retro 2026-11-16: the role guides total about 4100 words and reach every repository. These rules are already enforced in code: the verdict-line format and the block after `REVIEW_FAILURE_LIMIT` failed reviews (`src/chitty/store.py`), review independence (`--override-review-independence`), and, in `_prepare_review` in `src/chitty/run.py`, blocking a review whose worktree has uncommitted changes, failing a review on a conflict when merging `main`, and failing a branch that changes the config or the managed `AGENTS.md` block. Shorten each to one line or remove it from `src/chitty/roles/review.md` and `work.md`, relying on the error message, and make sure each error message says what to do.

## Notes

Implemented directly by the planning session as an untestable guide change, commit f83a70f.

Reviewed: untestable wording change, read by the planning session; make check passes.

Correction: the change landed on main as 8377661; the commit named above was wrong.

## History

- 2026-11-16T09:59:49Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:31Z intrepid-coral-raven backlog → planning
- 2026-11-16T10:50:29Z intrepid-coral-raven: changed description
- 2026-11-16T16:48:10Z open-russet-eel: changed labels, owner
- 2026-11-16T16:48:25Z open-russet-eel planning → todo
- 2026-11-17T18:28:44Z kind-umber-toad: changed notes
- 2026-11-17T18:28:44Z kind-umber-toad todo → review
- 2026-11-17T18:28:46Z kind-umber-toad: changed notes; overrode review independence
- 2026-11-17T18:28:46Z kind-umber-toad review → done
- 2026-11-17T18:28:48Z kind-umber-toad done → archived
- 2026-11-17T18:29:53Z kind-umber-toad: changed notes
