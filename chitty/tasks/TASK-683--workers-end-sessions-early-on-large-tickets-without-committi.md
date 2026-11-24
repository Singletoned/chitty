---
title: Workers end sessions early on large tickets without committing
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

On 2026-11-23 two tickets went to `error` with `still doing after 5 continuations with no new work committed`: TASK-557 (the worker committed a stub, then made no further commits) and TASK-598 (TASK-610's new output shows each session lasting about 23 s and ending with 'TASK-598 remains unfinished in doing ... implementation and the required tests remain outstanding'). TASK-557 was then finished by hand in one session, so the work fit one session; the worker was stopping by choice, not running out of room. Worth checking what the continuation prompt and work guide tell the agent, whether the worker model treats a long ticket as permission to stop, and whether a continuation should say plainly to keep going until the criteria pass or return the ticket to planning with a reason.

## Notes

Suggestion origin: chitty

Duplicate of TASK-562 (work agents stop early on larger tickets); the evidence is recorded there.

## History

- 2026-11-24T22:21:45Z zesty-coral-newt → backlog
- 2026-11-24T22:21:46Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:51Z zesty-coral-newt: changed labels, notes
