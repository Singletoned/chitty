---
title: Stop sessions reviewing their own work
status: done
priority: high
depends_on:
  - TASK-55
created: 2026-10-28
---

## Description

Agents are told never to review a ticket they worked on, but that relies on memory, which compaction and new sessions lose, and models lean towards approving their own work. Once every change records its actor (TASK-55), Chitty can enforce independence itself instead of trusting the agent.

Origin (circuitry): one session implemented `CIRCUIT-67`..`72`, then wrote "Reviewed:" notes and set them done. Subagents count as their parent for now, so a reviewer subagent does not make a review independent.

## Acceptance Criteria

- [x] An actor who wrote the plan, ticked criteria, or moved the task to `review` cannot pass it (`-s done`) or fail it (`-s doing`); the error names the actor and what they did
- [x] `chitty show` tells the caller when they worked on the task
- [x] Overriding needs an explicit flag, never a default, and the override is recorded in History
- [x] Subagents count as their parent
- [x] `review → done` requires a note starting `Reviewed:`, so skipping review is never silent

## Plan

Inspect the actor-attributed History support from TASK-55 and the status-transition paths. Add review-independence validation, explicit override recording, reviewer-note validation, and worked-on visibility in `show`; cover each rule with focused tests. Run the targeted tests and `make check`, then complete the ticket.

## Notes

Suggestion origin: circuitry

Needs refinement before promotion: determine whether Claude Code child sessions receive distinct `CLAUDE_CODE_SESSION_ID` values, define the compatibility policy for harnesses that do not expose identity, and split the actor-recording and review-enforcement work into independently verifiable tickets.

Split per the earlier refinement note: session identity is TASK-75, recording actors is TASK-55, and this ticket is only enforcement. The commit-trailer idea (`Session: <name>`) is dropped for now, since History will carry the actor.

Held until agents restart with session identity (HUMAN-5, via TASK-55).

Absorbed TASK-54's enforcement idea (require a `Reviewed:` note to pass a review); its guide-wording half is in TASK-91. TASK-54 is archived.

Blocked pending independent review and completion of `TASK-55`, which supplies the actor-attributed History entries required for enforcement.

`TASK-55` is done; unblocked.

Choice: History records only plan and criterion-tick events needed to establish reviewer involvement; `TASK-99` will extend actor-attributed events to all deliberate non-status edits. This keeps the enforcement scope small and is cheap to broaden.

Reviewed: verified independent-review enforcement, explicit override history, reviewer-note gating, caller visibility, and Pi parent identity; targeted tests pass.

## Summary

Implemented independent review enforcement, explicit recorded overrides, reviewer-note validation, current-actor worked-on output, and inherited Pi parent identity for subagents. Verified with `make check`, Pi extension tests, and `chitty fix` (existing repository warnings only).

## History

- 2026-10-28 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → backlog
- 2026-11-01 backlog → todo
- 2026-11-02T08:52:55Z pi-worker todo → blocked
- 2026-11-02T09:34:51Z lively-otter blocked → todo
- 2026-11-02T09:39:51Z amber-stoat todo → doing
- 2026-11-02T09:44:46Z amber-stoat doing → review
- 2026-11-02T09:44:46Z amber-stoat: ticked acceptance criteria
- 2026-11-02T11:21:23Z jolly-falcon: changed notes
- 2026-11-02T11:21:23Z jolly-falcon review → done
