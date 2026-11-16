---
title: Make cold reads a read-only scan
status: backlog
created: 2026-11-16
---

## Description

Retro of 2026-11-16: cold-read tickets passed their first review no more often than others (69% against 73%; since 2026-11-05, 69% against 79%), and the implementing read costs an extra agent session, repeated until a read finds nothing. Change `src/chitty/roles/plan.md` and `src/chitty/roles/cold-read.md` so a cold read is a single read-only pass by a fresh agent: it reads the ticket and referenced code and reports done meaning, likely files, open decisions, unverified behaviour, unhandled states and wrong claims. No throwaway worktree, no implementation, no repeat-until-clean. The proof that tests fail without the change moves to the runner (`TASK-338`). The safety net for anything a quick read misses is the existing return to planning (`TASK-323`): a worker or reviewer who finds the ticket missing, contradictory or undecided sends it back to `planning`. The guides should say this plainly, as the expected route rather than a failure.

## History

- 2026-11-16T09:50:16Z intrepid-coral-raven → backlog
- 2026-11-16T09:59:48Z intrepid-coral-raven: changed description
