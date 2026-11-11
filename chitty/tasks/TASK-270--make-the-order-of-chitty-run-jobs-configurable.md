---
title: Make the order of `chitty run` jobs configurable
status: backlog
parent: TASK-259
created: 2026-11-11
---

## Description

- Today `src/chitty/selection.py` picks `review`, then `doing`, then `todo` (`STATUSES`). Add a `job_order` setting in `chitty.toml` listing those statuses, plus `cold-read` once it exists.
- Default: `cold-read`, `review`, `doing`, `todo`. Cold reads come first because they hold up planning.

## History

- 2026-11-11T13:21:06Z vivid-yellowhammer → backlog
