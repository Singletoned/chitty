---
title: Decide how to handle missing review branches
status: backlog
parent: TASK-318
created: 2026-11-13
---

## Description

The review of `TASK-318` found a conflict: its criterion requires a missing branch to leave the ticket unchanged and invoke the reporter, while existing `tests/test_review_merge.py` deliberately expects a missing review branch to mark the ticket `blocked` and stop selection. Decide the intended behavior before writing a fix; an unchanged selectable review ticket may repeatedly fail. Refine and cold-read before implementation.

## History

- 2026-11-13T23:27:55Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:26Z mellow-umber-lapwing: changed title, description
