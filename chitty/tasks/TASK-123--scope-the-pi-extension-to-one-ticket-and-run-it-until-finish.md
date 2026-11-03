---
title: Scope the Pi extension to one ticket and run it until finished
status: todo
priority: high
parent: TASK-106
created: 2026-11-03
---

## Description

Make `pi --chitty-work TASK-12` and `pi --chitty-review TASK-12` take one ticket, keep going until that ticket has left the stage, then exit. Each ticket gets its own process, so its own actor, which is what makes reviews independent.

File: `src/chitty/integrations/pi/chitty.ts`, tests in `src/chitty/integrations/pi/tests/chitty.test.ts`. Pi's API is in the installed `@earendil-works/pi-coding-agent` package: `dist/core/extensions/types.d.ts` and `docs/extensions.md`.

Decisions:

- `chitty-work` and `chitty-review` become `type: "string"` flags, and `/chitty` becomes `/chitty work|review ID`. An ID is required. A flag with no ID, or an unknown ticket, is a loud error. Pass the ID to `chitty`, which accepts `task-12` and `12`.
- Remove the queue-draining mode: `hasActionableTickets`, `isActionableTicket`, the `NO MORE WORK` handling, and prompt text about choosing or moving on to other tickets. An agent works only the named ticket and does not pick another.
- Finished is read from the ticket, never from the agent's words: `chitty show ID --json` on `agent_settled`. Work is finished when status is no longer `todo` or `doing`. Review is finished when status is no longer `review`.
- If it is not finished, send a continuation prompt, as `/auto-continue` does. The prompt says that a question for a person means a note and `-s blocked`, not ending the turn. A module-level constant caps continuations at 5, as `auto-continue.ts` does, so a stuck agent cannot spend without limit.
- When finished, or at the cap, or when the last response has `stopReason` `error` (for example out of credits), call `ctx.shutdown()`. Say why first with `ctx.ui.notify`.
- If the human aborts (`event.aborted`), stop continuing and stay open: the human has taken over.

Pi's interactive `shutdown` always exits 0, so nothing can rely on the exit code. The caller compares ticket state instead (see the `chitty run` ticket).

Out of scope: choosing a ticket, looping, model selection per stage, creating worktrees for the agent.

## Acceptance Criteria

- [ ] Node tests cover flag and `/chitty` parsing: valid ID, missing ID, and unknown mode
- [ ] Node tests cover the decision after settling, for each mode: finished, unfinished, cap reached, `error`, and aborted
- [ ] A review prompt and a work prompt name the ticket and contain no instruction to select another ticket, with Node tests asserting it
- [ ] Run by hand against a scratch ticket: `pi --chitty-work <ID>` continues past a turn that leaves the ticket in `doing`, and exits once it reaches `review`. Record the result in a note
- [ ] `README.md` describes the new usage, and `__version__` is bumped so `chitty init` installs the extension

## History

- 2026-11-03T12:40:38Z lively-panda → todo
