---
title: Stop the work continuation prompt offering `planning` as an equal way out
status: todo
labels:
  - untestable
priority: high
owner: untestable
created: 2026-11-24
---

## Description

Workers under `chitty run` return sound tickets to `planning` with notes that deny any defect, for example "Ticket is implementable and no defect or external obstacle has been identified; implementation remains unfinished" (`TASK-629`, 2026-11-24) and "Implementation has not started. The ticket is actionable" (echonomicon `TASK-203`). Some return unfinished work of their own, such as missing tests (echonomicon `TASK-217`, `TASK-219`). Each return costs a planner session. Most cases ran `gpt-6-luna`; the work guide was rewritten and work sessions moved to terra on 2026-11-25, and `TASK-10000` escalates a third return to a person.

What remains is the prompt the runner sends to resume an unfinished work session, `continuation_prompt` in `src/chitty/run.py`. It reads "Either finish it and set it to `review`, return it to `planning` ..., or set it to `blocked` ...", offering three equal choices to an agent that has just stopped early, and does not say that its own unfinished work is not a defect.

Change the `work` branch of `continuation_prompt` to this text, keeping the f-string and the opening words `Continue working only on Chitty ticket ` that `tests/test_run_continue.py` checks:

> Continue working only on Chitty ticket {ticket_id} until it is finished and set to `review`. Your own unfinished work, including missing tests, is never a reason to stop or to return the ticket. Leave `doing` early only for a defect in the ticket text (`planning`, with a note giving the problem and the decision needed, or proposing a split if it is too large for one session) or an external obstacle (`blocked`, with a note giving it). There is no token, time or context budget.

This replaces the current sentences rather than adding to them; the prompt stays about the same length.

Out of scope: the `review` branch of `continuation_prompt`, the guides, and refusing a return in code.

## History

- 2026-11-24T22:21:48Z zesty-coral-newt → backlog
- 2026-11-24T22:21:49Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:31Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:55Z zesty-coral-newt: changed priority
- 2026-11-25T22:27:38Z golden-coral-stoat: replaced notes; changed title, labels, owner, description
- 2026-11-25T22:27:38Z golden-coral-stoat backlog → planning
- 2026-11-25T22:27:40Z golden-coral-stoat planning → todo
