---
title: Record which session did what, and stop sessions reviewing their own work
status: backlog
created: 2026-10-28
---

## Description

Problem: in circuitry, one agent session implemented CIRCUIT-67..72, then wrote "Reviewed:" notes and set them done. Chitty only records dates in History and free-text notes, so nothing showed or prevented that the implementer reviewed its own work. Every session commits as the same git user, so git cannot tell them apart either.

Constraint: agents cannot set environment variables for their session (each command runs in a fresh shell), so the identity must come from the harness, not from the agent.

What the harnesses already provide (checked 2026-10-28):
- Claude Code sets CLAUDE_CODE_SESSION_ID in every shell command's environment (also CLAUDE_CODE_CHILD_SESSION, meaning untested).
- Pi has PI_SESSION_ID, PI_MODEL and PI_PROVIDER, but removes them from shells unless the exposeSessionEnvironment setting is on.

Proposal:
1. Work out the actor on every write: CHITTY_ACTOR if set, else CLAUDE_CODE_SESSION_ID or PI_SESSION_ID (plus harness and model when known). Derive a stable readable name from a hash of the ID (e.g. "amber-heron"), so the same session always gets the same name with no stored state and nothing lost on compaction.
2. Record the actor on History lines ("doing -> review by amber-heron (claude-code 3f9a...)"), notes, plan writes and ticked criteria.
3. Enforce review independence: the actor who wrote the plan, ticked criteria or moved the ticket to review cannot move it to done or fail it back to doing. Overriding should need an explicit flag, never a default.
4. With no harness identity, refuse status changes unless --as NAME is given (for humans, other tools, CI). Fail loudly, not "unknown".
5. Document a commit trailer (e.g. "Session: amber-heron") alongside "Task: ID", so a reviewer can check whether it wrote any of a ticket's commits.

Open question: whether a Claude Code subagent gets its own session ID. A fresh-context reviewer subagent should count as a separate actor. One that inherits its parent's context should not. Test by having a subagent print CLAUDE_CODE_SESSION_ID and CLAUDE_CODE_CHILD_SESSION.

## Notes

Suggestion origin: circuitry

Needs refinement before promotion: determine whether Claude Code child sessions receive distinct `CLAUDE_CODE_SESSION_ID` values, define the compatibility policy for harnesses that do not expose identity, and split the actor-recording and review-enforcement work into independently verifiable tickets.

## History

- 2026-10-28 → backlog
