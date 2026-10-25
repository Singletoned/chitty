---
title: Add a backlog status for tickets that need refining
status: todo
labels:
  - cli
created: 2026-10-25
---

## Description

Like a backlog column on a kanban board: tickets that are real work but still need refining before anyone picks them up. Add a backlog status before todo (backlog → todo → doing → done) in every context. Capture with `chitty add TITLE -s backlog`; -d is optional there, and when omitted the Description gets a default text that says plainly the ticket needs refining. Refine with the usual edit flags; promote with `chitty edit ID -s todo`.

## Acceptance Criteria

- [ ] backlog is a status, ordered before todo, in every context
- [ ] chitty add -s backlog works without -d and writes a default Description saying the ticket needs refining
- [ ] add without -s backlog still requires -d
- [ ] The MCP add tool accepts status backlog with the same rules
- [ ] PLAN.md, README and the agent guide describe backlog

## Notes

Question for the task owner: What makes an idea distinct from an ordinary context/task? The proposed ideas context and optional Description conflict with the strict required Description format and TASK-6 needs a reliable, non-name-based way to hide ideas. No implementation will be chosen until this is decided.

Questions requiring a product decision:

1. Is `ideas` a reserved built-in context name, or should contexts gain explicit metadata (for example, kind = "ideas") so TASK-6 can hide them without name-based behavior?
2. When no description is supplied, what valid `## Description` content should be stored? Relaxing the required non-empty Description invariant would change the task-file format.
3. Should `chitty init` add the ideas context automatically, and how should existing repositories opt in?
4. Must idea capture have matching MCP support and JSON output like the other commands?

Open: should moving out of backlog be refused while the Description is still the default text? Leaning yes, but not decided.

Answers to the questions above: (1) neither a reserved context nor context metadata: backlog is a status, so every context has one. (2) The Description stays required; backlog tickets get a default text saying they need refining. (3) No init change; existing repos get it automatically. (4) Yes: add and edit already have MCP and JSON, so status backlog flows through both.
