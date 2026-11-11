---
title: Tell cold readers how to apply the planner's mutants
status: doing
parent: TASK-284
created: 2026-11-11
---

## Description

- `src/chitty/roles/plan.md` tells planners to use a fixed list of mutants for every read, but `src/chitty/roles/cold-read.md` does not mention them, so readers apply them only when the prompt explains how. When they did, they caught real gaps (TASK-284).
- Add to the cold-read guide: if the planner names mutants, after the tests pass apply each one alone to the implementation, run the ticket's tests, restore it, and report each survivor with criterion wording that would catch it. The report list also gains a bullet for survivors, each with that wording, or none.

## Acceptance Criteria

- [ ] A test in `tests/test_guide_cold_read_mutants.py` shows that in `chitty guide cold-read` the mutant step says one at a time, restore before the next, and criterion wording for survivors, and that the report list separately asks for survivors with that wording. It fails today.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-299/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T21:10:10Z vivid-yellow-raven → backlog
- 2026-11-11T21:10:21Z vivid-yellow-raven backlog → cold-read
- 2026-11-11T21:14:09Z vivid-yellow-raven: changed description
- 2026-11-11T21:14:12Z vivid-yellow-raven: changed acceptance criteria, notes
- 2026-11-11T21:14:12Z vivid-yellow-raven cold-read → todo
- 2026-11-11T22:07:10Z kind-lilac-toad todo → doing
