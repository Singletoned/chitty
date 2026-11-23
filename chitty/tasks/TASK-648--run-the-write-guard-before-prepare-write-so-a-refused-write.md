---
title: Run the write guard before `_prepare_write`, so a refused write cannot upgrade setup
status: backlog
depends_on:
  - TASK-385
parent: TASK-376
created: 2026-11-23
---

## Description

Split from `TASK-385` (2026-11-22 plan, part 4; old criterion 4 there). In `Repo.edit`, `move`, `archive` and `restore` in `src/chitty/store.py`, `_prepare_write()` runs before the lookup and `_require_writable`, so a write that is then refused can already have upgraded `chitty.toml` and committed it. Move `_prepare_write()` after the lookup and the guard, so the guard is the first thing that can refuse.

Old criterion, to refine when planned: with a stale `chitty_version` and autocommit on, a refused `chitty edit` of a ticket with a newer, different copy elsewhere leaves `HEAD` and `chitty.toml` unchanged (fails before the change).

## History

- 2026-11-23T14:35:36Z youthful-quartz-zander → backlog
