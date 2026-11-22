---
title: Squash bookkeeping commits when `chitty run` lands a ticket
status: backlog
depends_on:
  - TASK-339
  - TASK-574
created: 2026-11-22
---

## Description

After `TASK-339` lands (`git.squash_bookkeeping`), call it in `_land_locked` in `src/chitty/run.py` right after `git.add_task_trailers`, on every landing attempt, with the context directories relative to the main checkout. To be planned against what `TASK-339` lands.

## History

- 2026-11-22T10:10:57Z friendly-jade-stoat → todo
- 2026-11-22T10:11:46Z friendly-jade-stoat: changed description
- 2026-11-22T10:11:46Z friendly-jade-stoat todo → backlog
- 2026-11-22T10:14:11Z friendly-jade-stoat: changed dependencies
