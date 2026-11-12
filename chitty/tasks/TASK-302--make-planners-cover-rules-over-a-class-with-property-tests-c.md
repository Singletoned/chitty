---
title: Make planners cover rules over a class with property tests, cases or a stated reason
status: backlog
created: 2026-11-12
---

## Description

- Workers test what criteria name. TASK-289 said every Chitty error after config load is reported, but its criteria tested only the agent exiting 1, so argument errors went unreported and the defect surfaced only in review. TASK-266 said any prefix from every directory under `chitty/`, but no criterion varied where a directory exists, so a directory only on another branch failed three reviews.
- Add to `src/chitty/roles/plan.md` (the `chitty guide plan` text) a list of words that usually state a rule over a class:
  - universal: all, every, each, any, always, never, no, none, regardless, whatever;
  - exclusion: except, unless, other than, only, not;
  - combination: with or without, whether, either, both, in any order;
  - invariance: unchanged, same as, preserved, stays, round-trip, idempotent;
  - sources and places: wherever, from any directory, branch, prefix or status.
- When a description uses one for behaviour, the ticket does one of: (1) a property test criterion naming what to generate and what must hold, the default for more than about three members or several axes; (2) the description names every member and each has a case; (3) a sentence names the one code path every member goes through, so one case covers them.
- The cold-read guide (`src/chitty/roles/`, the `chitty guide cold-read` text) asks the reader to list each such rule with its treatment and to flag one with none, or a code-path claim that is false.

## History

- 2026-11-12T18:38:04Z kind-yellow-vole → backlog
