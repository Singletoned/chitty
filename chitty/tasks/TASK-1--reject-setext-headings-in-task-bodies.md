---
title: Reject setext headings in task bodies
status: done
labels:
  - parser
created: 2026-10-23
---

## Description

The body parser only recognises ATX headings. A line of text followed by `===` or `---` is a setext heading in CommonMark, so it can start a section the parser never sees (and prettier rewrites it as `#`/`##`).

## Acceptance Criteria

- [x] A setext heading outside a fence is a parse error naming the line
- [x] A thematic break after a blank line is still allowed

## Plan

Inspect the fence-aware body parser, reject setext heading syntax outside fences with an error that includes its line number, and add regression tests preserving valid thematic breaks.

## Notes

Question: Which setext underline forms currently escape section validation, and where should their source line be reported? I will answer this from the parser and tests before changing behavior.

Answer: _split_sections in src/chitty/model.py is fence-aware but treats every non-ATX line as content. Both = and - underline forms therefore escape validation. The underline source line is available during its existing enumerated loop; a blank preceding line distinguishes the required valid thematic break.

Verified: focused regression tests failed before the parser change; all parser behavior and the full make check suite now pass.
