---
title: Reject setext headings in task bodies
status: todo
labels:
  - parser
created: 2026-10-23
---

## Description

The body parser only recognises ATX headings. A line of text followed by `===` or `---` is a setext heading in CommonMark, so it can start a section the parser never sees (and prettier rewrites it as `#`/`##`).

## Acceptance Criteria

- [ ] A setext heading outside a fence is a parse error naming the line
- [ ] A thematic break after a blank line is still allowed
