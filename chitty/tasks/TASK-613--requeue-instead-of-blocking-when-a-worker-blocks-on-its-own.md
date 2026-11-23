---
title: Requeue instead of blocking when a worker blocks on its own budget
status: backlog
created: 2026-11-23
---

## Description

In taidy on 2026-11-22, two workers (`pi` with `--model gpt-6.1-terra`, via `chitty run --loop --mode work`) set TASK-12 and TASK-24 to `blocked` within about a minute and ten tool calls, with notes like "this worker cannot complete the required implementation ... within its available execution budget; a new worker is needed". Token usage in the pi session log (`~/.pi/agent/sessions/--Users-singletoned-src-singletoned-taidy-.worktrees-task-12--/`) was tiny, so the claim was false. `blocked` is meant for external obstacles needing a human, so the loop stalled until a human reset them. Suggestions: (1) the work guide should say that running out of time or context is not a blocker: leave the ticket in `doing` with a progress note and exit; (2) when a run ends with the ticket in `doing`, the runner clears the owner and requeues it, perhaps with a retry cap before `error`. The same TASK-12 worker also ran `git reset --hard main` on its ticket branch to get past a "latest version is on main" refusal; the guide could name the safe fix (rebase onto `main`).

## Notes

Suggestion origin: taidy

## History

- 2026-11-23T10:24:07Z witty-russet-gannet → backlog
- 2026-11-23T10:24:08Z witty-russet-gannet: changed notes
