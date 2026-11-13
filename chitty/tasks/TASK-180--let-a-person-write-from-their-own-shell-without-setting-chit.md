---
title: Let a person write from their own shell without setting `CHITTY_ACTOR`
status: backlog
priority: low
created: 2026-11-05
---

## Description

`actor()` in `src/chitty/actor.py` raises `cannot determine actor` outside an agent session, so `chitty edit TASK-142 -s doing` failed when the human ran it on 2026-11-05. Decide what a person's actor should be before this is refined. A fallback must not credit an unsupported agent's writes to a person.

## Notes

Reproduced on 2026-11-13 in `echonomicon`: `uv run chitty run --loop --mode work -- --model gpt-6-luna` failed before starting the run with `cannot determine actor; set CHITTY_ACTOR or provide one of CLAUDE_CODE_SESSION_ID, CHITTY_PI_SESSION_ID, PI_SESSION_ID, CODEX_THREAD_ID, CODEX_SESSION_ID`. This is the same underlying human-shell case: `chitty run` resolves the actor while preparing its error context, before assigning its generated run actor.

## History

- 2026-11-05T09:37:44Z mellow-newt → backlog
- 2026-11-13T10:29:08Z lively-violet-puffin: changed notes
