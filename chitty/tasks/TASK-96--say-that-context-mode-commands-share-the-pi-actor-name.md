---
title: Say that context-mode commands share the Pi actor name
status: done
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

Reviewed: inspected commit `dd0e318`; both required documents accurately distinguish context-mode's post-`session_start` execution from servers started earlier. Independently confirmed `ctx_execute` and shell `chitty whoami` both report `pi-reviewer`; `make check` passes (183 tests).

## History

- 2026-11-01 → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
