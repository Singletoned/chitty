---
title: Let `chitty run --mode` be given more than once
status: backlog
parent: TASK-259
created: 2026-11-11
---

## Description

- `chitty run --mode work --mode review` takes whichever job comes first in the job order across those modes. One `--mode` behaves as today; none means every mode.
- Applies to `chitty next --mode` too, and to MCP if it takes a mode.

## History

- 2026-11-11T13:21:05Z vivid-yellowhammer → backlog
