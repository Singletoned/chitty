---
title: Scope the Pi extension to one ticket and run it until finished
status: doing
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

- [x] Node tests cover flag and `/chitty` parsing: valid ID, missing ID, and unknown mode
- [ ] Node tests cover the decision after settling, for each mode: finished, unfinished, cap reached, `error`, and aborted
- [x] A review prompt and a work prompt name the ticket and contain no instruction to select another ticket, with Node tests asserting it
- [x] Run by hand against a scratch ticket: `pi --chitty-work <ID>` continues past a turn that leaves the ticket in `doing`, and exits once it reaches `review`. Record the result in a note
- [x] `README.md` describes the new usage, and `__version__` is bumped so `chitty init` installs the extension

## Plan

Inspect the current Pi extension and its Node tests, then add focused parser, prompt, and settlement tests before implementing the one-ticket continuation loop. Update the extension, documentation, and version; verify the requested scratch-ticket flow and `make check` before handing the ticket to review.

## Notes

Manual verification: in scratch repository `/tmp/chitty-task-123-TLk9qR`, launched `pi --no-extensions --extension /Users/singletoned/src/singletoned/chitty/.worktrees/task-123/src/chitty/integrations/pi/chitty.ts --chitty-work TASK-1`. The first turn committed `TASK-1` as `doing`; the extension sent its continuation; the next turn moved it to `review`; Pi notified `ticket left work with status review` and shut down with exit `0`.

Review failed: an unknown `--chitty-work` or `--chitty-review` ID starts an agent turn before `ticketStatus()` runs at `agent_settled`; only after that turn does `chitty show <ID> --json` fail. Validate the named ticket before `start()` sends its prompt, and add a regression test proving an unknown ID is rejected without starting an agent turn.

Verified unknown --chitty-work and --chitty-review IDs fail during session startup before any agent turn; regression test added. Ran npm test and make check.

Review failed: starting  for a ticket already outside / (or  for one outside ) still sends an agent turn.  reads and discards the status before , so it cannot immediately notify and shut down as required once the named ticket has left its stage. Handle inactive status at startup and add a regression test that verifies no agent turn starts.

Review clarification: the preceding note lost its code spans because the review command shell expanded backticks. Starting `pi --chitty-work` for a ticket already outside `todo`/`doing` (or `pi --chitty-review` for one outside `review`) still sends an agent turn. `start()` reads and discards the status before `sendUserMessage()`, so it cannot immediately notify and shut down once the named ticket has left its stage. Handle inactive status at startup and add a regression test that verifies no agent turn starts.

## Summary

Scoped Pi work and review runs to one ticket, added continuation-state tests, documented the ID-based commands, and bumped to `0.1.20`. Verified with `npm test`, `make check`, and a scratch Pi run that continued from `doing` then shut down after `review`.

## History

- 2026-11-03T12:40:38Z lively-panda → todo
- 2026-11-03T13:28:06Z kind-badger: wrote the plan
- 2026-11-03T13:28:06Z kind-badger todo → doing
- 2026-11-03T14:00:10Z kind-badger: changed notes; ticked acceptance criteria
- 2026-11-03T14:01:49Z kind-badger: changed summary
- 2026-11-03T14:01:49Z kind-badger doing → review
- 2026-11-03T14:27:01Z lively-lynx: changed acceptance criteria, notes
- 2026-11-03T14:27:01Z lively-lynx review → doing
- 2026-11-03T15:35:39Z jolly-badger: ticked acceptance criteria
- 2026-11-03T15:35:52Z jolly-badger: changed notes
- 2026-11-03T15:35:52Z jolly-badger doing → review
- 2026-11-03T15:47:15Z lively-koala: changed acceptance criteria, notes
- 2026-11-03T15:47:15Z lively-koala review → doing
- 2026-11-03T15:47:27Z lively-koala: changed notes
