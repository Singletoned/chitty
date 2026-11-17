---
title: Tell workers and reviewers to list every problem when returning a ticket to planning
status: done
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-360
created: 2026-11-16
---

## Description

`src/chitty/roles/review.md` already says to report all findings from a review pass together, but the planning return in `work.md` and `review.md` does not. With read-only cold reads (`TASK-336`), the return to planning becomes the main way ticket problems are found, and returning them one at a time costs a planning round each. Add to both guides: before setting `-s planning`, finish reading the ticket and the code it touches, and list every missing, contradictory or undecided requirement found in that one note. Keep it to one sentence in each guide.

## Notes

Implemented directly by the planning session as an untestable guide change, commit ff0021f.

Reviewed: untestable wording change, read by the planning session; make check passes.

Correction: the change landed on main as 8377661; the commit named above was wrong.

## History

- 2026-11-16T10:19:38Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:53Z intrepid-coral-raven backlog → planning
- 2026-11-16T12:51:08Z open-russet-eel: changed dependencies
- 2026-11-16T16:48:14Z open-russet-eel: changed labels, owner
- 2026-11-16T16:48:29Z open-russet-eel planning → todo
- 2026-11-17T18:28:57Z kind-umber-toad: changed notes
- 2026-11-17T18:28:57Z kind-umber-toad todo → review
- 2026-11-17T18:28:59Z kind-umber-toad: changed notes; overrode review independence
- 2026-11-17T18:28:59Z kind-umber-toad review → done
- 2026-11-17T18:29:02Z kind-umber-toad done → archived
- 2026-11-17T18:29:58Z kind-umber-toad: changed notes
