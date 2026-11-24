---
title: Detect Antigravity sessions via ANTIGRAVITY_CONVERSATION_ID for actor resolution
status: backlog
created: 2026-11-24
---

## Description

When running `chitty add` from Google Antigravity CLI, actor resolution fails with:

```text
Error: cannot determine actor; set CHITTY_ACTOR or provide one of CLAUDE_CODE_SESSION_ID, CHITTY_PI_SESSION_ID, PI_SESSION_ID, CODEX_THREAD_ID, CODEX_SESSION_ID
```

Antigravity sets `ANTIGRAVITY_CONVERSATION_ID` (and `ANTIGRAVITY_AGENT`) in the process environment. Supporting `ANTIGRAVITY_CONVERSATION_ID` alongside `CLAUDE_CODE_SESSION_ID`, `PI_SESSION_ID`, and `CODEX_SESSION_ID` would give Antigravity sessions an automatic stable actor name without requiring `CHITTY_ACTOR=...` before every `chitty` invocation (which also keeps `chitty <subcommand>` commands prefix-matchable for tool approvals).

## Notes

Suggestion origin: shelfpath

## History

- 2026-11-24T22:21:22Z zesty-coral-newt → backlog
- 2026-11-24T22:21:22Z zesty-coral-newt: changed notes
