---
title: "Plan guide: verify new claims before a cold-read reread, and split after a third failed read"
status: backlog
created: 2026-11-19
---

## Description

In the ticket-state migration planning session (2026-11-18, 29 tickets, recorded in `docs/plan/pipeline-and-feedback.md` under Cold read), tickets took about 2.5 Haiku reads each, up to 13 for `TASK-378` and its splits. Most later-round findings were errors the planner fixes had introduced: a `chitty restore` command that does not exist, wrong test base classes, a spy on `git.main_checkout`, which `_main_branch()` calls legitimately, and a false claim that merged `task-*` branches exist. Proposal: `chitty guide plan` should tell the planner to check each new claim about code, commands or tests against the source before asking for another read, and to split a ticket whose third read still finds problems rather than patch it again.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:03Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:04Z sunny-white-dormouse: changed notes
