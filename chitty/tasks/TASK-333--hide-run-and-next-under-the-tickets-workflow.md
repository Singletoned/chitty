---
title: Hide run and next under the tickets workflow
status: planning
labels:
  - needs-minor
depends_on:
  - TASK-331
created: 2026-11-14
---

## Description

Under `workflow = "tickets"`, hide the runner commands.

- `chitty run` and `chitty next` are absent from `chitty --help`, and the MCP server does not list its `next` tool.
- Invoking either still fails loudly, exit 1, with a message naming the command and saying it needs `workflow = "runner"` in the config, rather than "no such command". The MCP `next` tool, if called by name, returns the same message as an error.
- Outside a Chitty repository, where there is no config, `chitty --help` lists every command.
- Under `workflow = "runner"` nothing changes.

## Acceptance Criteria

- [ ] Under `tickets`, `chitty --help` lists neither `run` nor `next`, and the MCP tool list has no `next`.
- [ ] Under `tickets`, `chitty run` and `chitty next` exit 1 with a message naming the command and `workflow = "runner"`; calling the MCP `next` tool returns that message as an error.
- [ ] Outside a Chitty repository and under `runner`, help output and behaviour are unchanged.
- [ ] CLI and MCP tests cover criteria 1 to 3, and fail without the change.

## History

- 2026-11-14T18:21:57Z friendly-ginger-adder → planning
