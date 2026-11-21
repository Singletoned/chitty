---
title: Let workers resolve small edge cases without returning to planning
status: planning
labels:
  - untestable
owner: untestable
created: 2026-11-21
---

## Description

The Chitty inbox suggestion “Work guide: let workers settle small edge cases and record them” points to `TASK-391`: several workers returned it to planning for individual edge cases that the planner could settle from existing repository behaviour. For example, the renumbering operation can retain the existing refusal to write outside Git when `autocommit` is enabled, if the ticket does not say otherwise. A real contradiction, or a ticket too large to finish in one session, still needs planning; this guidance does not replace splitting the work.

Revise `src/chitty/roles/work.md` so workers resolve a small, cheap-to-reverse omission in place only when the ticket and existing code or tests point to one clear default. The choice must preserve stated requirements and acceptance criteria and must not introduce a new user-visible policy, command, or setting. Have the worker add a ticket note in the form `Decided: <case> -> <choice>, because <reason>`, cite the precedent, and cover the resolved edge case with a focused test where testable. This does not let a worker invent or weaken a test needed to verify a stated criterion. Return to `planning` for contradictions, unclear or consequential choices, and other ticket defects; finish the read and report all blockers in one note rather than returning once per discovery.

Align `src/chitty/roles/review.md` so reviewers check the recorded choice, its precedent and any test against the same boundary. A choice within the boundary does not require planning simply because the ticket did not spell it out. Keep the existing distinction between implementation defects (`doing`) and ticket defects (`planning`). Reflect the same exception in `src/chitty/guide-runner.md` (the source of the managed `AGENTS.md` block; do not hand-edit that block) and `docs/plan/pipeline-and-feedback.md`.

This is a wording-only change. Keep the guidance general across repositories and preserve the existing tested return routes. No changes to runner behaviour, status rules, or `TASK-391` itself.

## History

- 2026-11-21T15:27:59Z friendly-ochre-wren → backlog
- 2026-11-21T15:28:14Z friendly-ochre-wren: changed description
- 2026-11-21T15:28:14Z friendly-ochre-wren backlog → planning
