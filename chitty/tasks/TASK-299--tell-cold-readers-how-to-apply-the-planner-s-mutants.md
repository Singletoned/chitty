---
title: Tell cold readers how to apply the planner's mutants
status: cold-read
parent: TASK-284
created: 2026-11-11
---

## Description

- `src/chitty/roles/plan.md` tells planners to use a fixed list of mutants for every read, but `src/chitty/roles/cold-read.md` does not mention them, so readers apply them only when the prompt explains how. When they did, they caught real gaps (TASK-284).
- Add to the cold-read guide: if the planner names mutants, after the tests pass apply each one alone to the implementation, run the ticket's tests, restore it, and report each survivor with criterion wording that would catch it. The report list also gains a bullet for survivors, each with that wording, or none.

## Acceptance Criteria

- [ ] A test shows `chitty guide cold-read` containing the mutant steps: one at a time, restore, and report survivors with criterion wording. It fails today.

## History

- 2026-11-11T21:10:10Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:21Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:14:09Z vivid-yellow-raven: changed description
