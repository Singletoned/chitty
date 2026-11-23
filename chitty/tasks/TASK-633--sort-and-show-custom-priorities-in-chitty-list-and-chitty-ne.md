---
title: Sort and show custom priorities in `chitty list` and `chitty next`
status: backlog
depends_on:
  - TASK-632
parent: TASK-607
created: 2026-11-23
---

## Description

Where `chitty list` and `chitty next` order or display by priority (`src/chitty/selection.py`, the list glyphs), use the configured order from `priorities`. Decide while planning how a custom priority is displayed (today each built-in value has a glyph): a derived short label or an optional glyph in config. Check against TASK-576 (natively wide glyphs only).

## History

- 2026-11-23T10:40:41Z witty-russet-gannet → backlog
