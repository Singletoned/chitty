---
title: Tell workers and reviewers to list every problem when returning a ticket to planning
status: planning
created: 2026-11-16
---

## Description

`src/chitty/roles/review.md` already says to report all findings from a review pass together, but the planning return in `work.md` and `review.md` does not. With read-only cold reads (`TASK-336`), the return to planning becomes the main way ticket problems are found, and returning them one at a time costs a planning round each. Add to both guides: before setting `-s planning`, finish reading the ticket and the code it touches, and list every missing, contradictory or undecided requirement found in that one note. Keep it to one sentence in each guide.

## History

- 2026-11-16T10:19:38Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:53Z intrepid-coral-raven backlog → planning
