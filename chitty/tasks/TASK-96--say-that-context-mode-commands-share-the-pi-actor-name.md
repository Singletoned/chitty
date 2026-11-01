---
title: Say that context-mode commands share the Pi actor name
status: review
priority: medium
created: 2026-11-01
---

## Description

`README.md` and `PLAN.md` say servers started before the extension need `CHITTY_ACTOR`, which suggests context-mode does. Verified on 2026-11-01 with context-mode 1.0.169: its MCP server starts at `before_agent_start`, after Chitty's `session_start` sets `CHITTY_PI_SESSION_ID`, and its executor passes the variable through. `pi -p` running `chitty whoami` gave the same name from the bash tool and from `ctx_execute`.

## Acceptance Criteria

- [x] `README.md` and `PLAN.md` say context-mode's `ctx_execute` shares the Pi actor name, and keep `CHITTY_ACTOR` only for servers that really start before `session_start`

## Plan

Edit the two passages; docs only, so no version bump (`chitty init` does not ship them).

## Notes

Also seen in the same test: Pi started from a Claude Code shell inherits `CLAUDE_CODE_SESSION_ID`, which Chitty checks first, so it took the Claude session's name. Rare, so not fixed here.

Implemented by lively-otter (Claude Code); `make check` passes.

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
