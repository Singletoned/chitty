---
title: Add a command for capturing ideas
status: todo
labels:
  - cli
created: 2026-10-25
---

## Description

A quick way to record ideas for future tickets that need more thought before they are real tasks: probably an ideas context, with the description optional (add currently requires -d).

## Notes

Question for the task owner: What makes an idea distinct from an ordinary context/task? The proposed ideas context and optional Description conflict with the strict required Description format and TASK-6 needs a reliable, non-name-based way to hide ideas. No implementation will be chosen until this is decided.

Questions requiring a product decision:

1. Is `ideas` a reserved built-in context name, or should contexts gain explicit metadata (for example, kind = "ideas") so TASK-6 can hide them without name-based behavior?
2. When no description is supplied, what valid `## Description` content should be stored? Relaxing the required non-empty Description invariant would change the task-file format.
3. Should `chitty init` add the ideas context automatically, and how should existing repositories opt in?
4. Must idea capture have matching MCP support and JSON output like the other commands?
