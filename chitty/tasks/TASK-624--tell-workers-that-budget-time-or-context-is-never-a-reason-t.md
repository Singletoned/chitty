---
title: Tell workers that budget, time or context is never a reason to block
status: done
labels:
  - untestable
owner: friendly-zinc-dormouse
created: 2026-11-23
---

## Description

Workers in taidy (`pi` with `gpt-6.1-terra` under `chitty run --mode work`, 2026-11-22) set three taidy tickets (taidy numbers 12, 24 and 30, not this repository's) to `blocked` with notes such as "this worker has insufficient execution budget". The claims were false: each session had used 11-17 thousand tokens and made no edits, and nothing in the prompt mentions a budget. Under 0.7.0 the same tickets ran, but the model still invented a budget limit when it stalled. `blocked` means an external obstacle needing a person, so each false block stalls the loop.

Change both places a worker reads:

- `src/chitty/roles/work.md`, the `-s blocked` bullet (about line 48): say that the session has no token, time or context budget for the worker to manage, and that budget, capacity, time or context is never a reason for `blocked`. A ticket too large for one session goes to `planning` with a note proposing a split.
- `continuation_prompt` in `src/chitty/run.py` (work mode): add the same point in one sentence. Its "Do not stop with it unfinished" may push a stalled model toward inventing an obstacle, so name the `planning` route for a ticket that is too large.

Keep the wording general (the guides reach every repository). Keep `tests/test_guide_return_to_planning.py` passing.

Out of scope: rejecting blocked notes by wording, and requeueing a ticket left in `doing` (TASK-617).

## Notes

Suggestion origin: taidy

Folded in from TASK-606 (follow-up) and TASK-613: under Chitty 0.7.0 the same TASK-24 ran in one session, but the model still invented a budget limit when it stalled, so the guide and prompt wording is still needed. The runner requeue half of TASK-613 is covered by TASK-617.

Reviewed: the `-s blocked` bullet in `work.md` says there is no token, time or context budget and that none of these is a reason for `blocked`. The too-large route to `planning` gains "(propose a split)", kept inside the 620-word budget. The work-mode `continuation_prompt` in `run.py` adds the same point and names the `planning` route. `make check` passed (1170 tests), including `tests/test_guide_return_to_planning.py`. Nit, not blocking: `work.md` line 29 now runs past the 80-column wrap of the lines around it.

## Summary

In `src/chitty/roles/work.md`, the `-s blocked` bullet now says the session has no token, time or context budget to manage, and that budget, capacity, time or context is never a reason for `blocked`. Rather than adding a separate bullet, which would exceed the 620-word budget for `work.md` (now 615), the existing too-large-ticket route to `planning` gains "(propose a split)".

The work-mode `continuation_prompt` in `src/chitty/run.py` adds one sentence: there is no token, time or context budget, so none is an obstacle, and a ticket too large for one session goes to `planning` with a note proposing a split.

Verification: `make check` passed (1170 tests), including `tests/test_guide_return_to_planning.py`. No test pins the prompt wording.

## History

- 2026-11-23T10:24:24Z witty-russet-gannet → backlog
- 2026-11-23T10:24:25Z witty-russet-gannet: changed notes
- 2026-11-23T10:27:30Z witty-russet-gannet: changed notes
- 2026-11-23T10:29:54Z witty-russet-gannet: changed title, labels, owner, description
- 2026-11-23T10:29:54Z witty-russet-gannet backlog → todo
- 2026-11-23T10:30:02Z witty-russet-gannet: changed description
- 2026-11-23T12:01:34Z friendly-zinc-dormouse: changed owner
- 2026-11-23T12:01:34Z friendly-zinc-dormouse todo → doing
- 2026-11-23T12:23:16Z friendly-zinc-dormouse: changed summary
- 2026-11-23T12:23:16Z friendly-zinc-dormouse doing → review
- 2026-11-23T13:32:49Z able-amber-falcon: changed notes
- 2026-11-23T13:32:49Z able-amber-falcon review → done
