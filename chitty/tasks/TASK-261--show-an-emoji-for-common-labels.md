---
title: Show an emoji for common labels
status: backlog
created: 2026-11-11
---

## Description

- `chitty list` prints labels as text, for example `[bug]`. Show an emoji for common ones, such as `bug` and `needs-discussion`, as statuses and priorities already have.
- Labels are shown in `src/chitty/cli.py` (`label_text`); status glyphs are `STATUS_GLYPHS` in `src/chitty/model.py`.
- Open: a fixed map in `model.py`, or one set in `chitty.toml`; and which labels get one.

## History

- 2026-11-11T10:37:05Z vivid-yellowhammer → backlog
