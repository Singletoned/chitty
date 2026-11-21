---
title: Let workers resolve small edge cases without returning to planning
status: review
labels:
  - untestable
owner: nimble-umber-adder
created: 2026-11-21
---

## Description

The Chitty inbox suggestion “Work guide: let workers settle small edge cases and record them” points to `TASK-391`: several workers returned it to planning for individual edge cases that the planner could settle from existing repository behaviour. For example, the renumbering operation can retain the existing refusal to write outside Git when `autocommit` is enabled, if the ticket does not say otherwise. A real contradiction, or a ticket too large to finish in one session, still needs planning; this guidance does not replace splitting the work.

Revise `src/chitty/roles/work.md` so workers resolve a small, cheap-to-reverse omission in place only when the ticket and existing code or tests point to one clear default. The choice must preserve stated requirements and acceptance criteria and must not introduce a new user-visible policy, command, or setting. Have the worker add a ticket note in the form `Decided: <case> -> <choice>, because <reason>`, cite the precedent, and cover the resolved edge case with a focused test where testable. This does not let a worker invent or weaken a test needed to verify a stated criterion. Return to `planning` for contradictions, unclear or consequential choices, and other ticket defects.

Make the return-to-planning instructions explicit for both workers and reviewers: finding the first blocker is a reason to stop implementation, not to stop investigating. Before changing status, finish reading the whole ticket and inspect the relevant code and tests for the remaining requirements. Gather as many actionable planning issues as that pass can uncover in one note, with the evidence and the decision or correction needed for each. If one blocker prevents checking another part, say what could not be checked and why; continue with independent parts. Do not speculate or expand the ticket's scope to fill out the note.

Align `src/chitty/roles/review.md` so reviewers check the recorded choice, its precedent and any test against the same boundary. A choice within the boundary does not require planning simply because the ticket did not spell it out. Keep the existing distinction between implementation defects (`doing`) and ticket defects (`planning`). Reflect the same exception in `src/chitty/guide-runner.md` (the source of the managed `AGENTS.md` block; do not hand-edit that block) and `docs/plan/pipeline-and-feedback.md`.

This is a wording-only change. Keep the guidance general across repositories and preserve the existing tested return routes. No changes to runner behaviour, status rules, or `TASK-391` itself.

## Plan

Update the worker, reviewer, managed runner source, and pipeline docs together. Spell out the narrow precedent-based exception, how to record and review it, and how to finish investigating before returning a ticket to planning. Keep the existing return routes and their tested wording, and leave the generated block and runtime code alone. Run the existing checks.

## Notes

Decided: the literal installed-guide snapshot -> update it to the new runner wording, because the existing workflow tests compare the full rendered guide byte for byte. `tests/test_guide_workflow_block.py` keeps those exact comparisons. The return-route assertions are unchanged.

## Summary

The work, review, and runner guides and pipeline docs now allow small, reversible omissions to be resolved using clear repository precedent, with a decision note and focused test where testable. They also explain how to finish investigating and report all actionable blockers before returning a ticket to planning. The role guides stay within their existing word budgets. Refreshed the literal runner guide fixture without changing assertions or the managed block in `AGENTS.md`. No runner behavior or status rules changed. `make format`, the 83 guide tests, and `make check` (976 tests) passed.

## History

- 2026-11-21T15:27:59Z friendly-ochre-wren → backlog
- 2026-11-21T15:28:14Z friendly-ochre-wren: changed description
- 2026-11-21T15:28:14Z friendly-ochre-wren backlog → planning
- 2026-11-21T15:28:27Z friendly-ochre-wren planning → todo
- 2026-11-21T15:43:39Z friendly-ochre-wren: changed description
- 2026-11-21T16:16:15Z nimble-umber-adder: changed owner; wrote the plan
- 2026-11-21T16:16:15Z nimble-umber-adder todo → doing
- 2026-11-21T16:18:05Z nimble-umber-adder: changed notes
- 2026-11-21T16:25:22Z nimble-umber-adder: changed summary
- 2026-11-21T16:25:22Z nimble-umber-adder doing → review
