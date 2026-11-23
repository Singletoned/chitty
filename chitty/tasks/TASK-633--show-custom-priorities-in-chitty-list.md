---
title: Show custom priorities in `chitty list`
status: backlog
depends_on:
  - TASK-632
parent: TASK-607
created: 2026-11-23
---

## Description

Part of TASK-607. TASK-632 adds the configured `priorities` list and the ordering. Until this ticket lands, `chitty list` shows a glyph only for `high`, `medium` and `low`, and an empty column for any other priority. Decide while planning how a custom priority is displayed: for example, a derived short label, or an optional glyph per name in config. Check against TASK-576 (natively wide glyphs only).

## Notes

Planner, 2026-11-23: ordering moved into TASK-632 after the person decided that `priorities` is an ordered list with `""` for no priority. This ticket covers display only.

## History

- 2026-11-23T10:40:41Z witty-russet-gannet → backlog
- 2026-11-23T12:37:55Z witty-russet-gannet: changed title, description, notes
