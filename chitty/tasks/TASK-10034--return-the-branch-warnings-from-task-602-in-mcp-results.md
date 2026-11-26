---
title: Return the branch warnings from TASK-602 in MCP results
status: backlog
depends_on:
  - TASK-602
created: 2026-11-25
moved_from: TASK-N6YMT2
---

## Description

Split from TASK-602 on 2026-11-25 to keep it small. TASK-602 and TASK-10040 put `<ID> also changed on <ref> ...` warnings in `Change.warnings`, which CLI `edit`, `note` and `archive <ID>` print. The MCP tools of the same names (`src/chitty/mcp.py`) share the store code but have no stderr for the agent to read, so they should add a `warnings` list to their results when there are any. Plan once TASK-602 lands, using the store method it settles on.

## History

- 2026-11-25T23:30:44Z calm-ochre-quail → backlog
- 2026-11-25T23:32:09Z calm-ochre-quail: renumbered from TASK-N6YMT2
- 2026-11-26T18:02:47Z brisk-bronze-adder: changed dependencies, description
