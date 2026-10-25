---
title: Make task IDs case-insensitive
status: todo
labels:
  - ids
created: 2026-10-25
---

## Description

Accept human-1 as HUMAN-1 everywhere an ID is taken (CLI, MCP, depends_on), or switch to lowercase IDs throughout. Decide which; IDs are currently upper-case only (ID_RE, PREFIX_RE).
