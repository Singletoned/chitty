---
title: Accept the `dropped` status through MCP
status: backlog
depends_on:
  - TASK-599
created: 2026-11-22
---

## Description

Split from `TASK-599` (the `dropped` status for the CLI and model) after its third cold read, 2026-11-22. Add `dropped` to the MCP `Status` `Literal` in `src/chitty/mcp.py`, so the MCP edit and add tools accept it with the same rules as the CLI (needs a non-empty Summary after the edit; refused from `done`). Tests in `tests/test_mcp.py`: the edit tool with `status="dropped"` and a summary changes the file; without a summary it is refused and the file is unchanged.

## History

- 2026-11-22T22:12:53Z plucky-umber-wren → backlog
