---
title: "Add a `difficulty` field to tickets: `low`, `medium` or `high`"
status: backlog
parent: TASK-308
created: 2026-11-12
---

## Description

- Like `priority`: optional, a closed set, validated, set with `chitty add --difficulty` and `chitty edit --difficulty` (`''` unsets), shown by `chitty show` and in MCP and JSON output.
- A field rather than a label: the set is closed and validated, and `priority` is the precedent.
- Whether `chitty list` shows it is open.

## History

- 2026-11-12T21:44:03Z kind-yellow-vole → backlog
