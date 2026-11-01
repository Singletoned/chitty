---
title: Stop sessions reviewing their own work
status: backlog
depends_on:
  - TASK-55
created: 2026-10-28
---

## Description

Agents are told never to review a ticket they worked on, but that relies on memory, which compaction and new sessions lose, and models lean towards approving their own work. Once every change records its actor (TASK-55), Chitty can enforce independence itself instead of trusting the agent.

Origin (circuitry): one session implemented `CIRCUIT-67`..`72`, then wrote "Reviewed:" notes and set them done. Subagents count as their parent for now, so a reviewer subagent does not make a review independent.

## Acceptance Criteria

- [ ] An actor who wrote the plan, ticked criteria, or moved the task to `review` cannot pass it (`-s done`) or fail it (`-s doing`); the error names the actor and what they did
- [ ] `chitty show` tells the caller when they worked on the task
- [ ] Overriding needs an explicit flag, never a default, and the override is recorded in History
- [ ] Subagents count as their parent

## Notes

Suggestion origin: circuitry

Needs refinement before promotion: determine whether Claude Code child sessions receive distinct `CLAUDE_CODE_SESSION_ID` values, define the compatibility policy for harnesses that do not expose identity, and split the actor-recording and review-enforcement work into independently verifiable tickets.

Split per the earlier refinement note: session identity is TASK-75, recording actors is TASK-55, and this ticket is only enforcement. The commit-trailer idea (`Session: <name>`) is dropped for now, since History will carry the actor.

## History

- 2026-10-28 → backlog
