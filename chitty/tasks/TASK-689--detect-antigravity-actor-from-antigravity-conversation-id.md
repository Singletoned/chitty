---
title: Detect Antigravity actor from `ANTIGRAVITY_CONVERSATION_ID`
status: backlog
created: 2026-11-24
---

## Description

Running `chitty add` from an Antigravity (`agy`) agent session fails with:

`Error: cannot determine actor; set CHITTY_ACTOR or provide one of CLAUDE_CODE_SESSION_ID, CHITTY_PI_SESSION_ID, PI_SESSION_ID, CODEX_THREAD_ID, CODEX_SESSION_ID`

Antigravity sets `ANTIGRAVITY_CONVERSATION_ID` (as well as `ANTIGRAVITY_AGENT` and `ANTIGRAVITY_TRAJECTORY_ID`) in the command environment. Recognising `ANTIGRAVITY_CONVERSATION_ID` in Chitty's actor-session detection would let Antigravity sessions use `chitty` out of the box without manually exporting `CHITTY_ACTOR` on every command.

## Notes

Suggestion origin: circuitry

## History

- 2026-11-24T22:21:51Z zesty-coral-newt → backlog
- 2026-11-24T22:21:52Z zesty-coral-newt: changed notes
