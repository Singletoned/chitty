---
title: Make print-mode Pi the default agent in this repository
status: backlog
owner: human
depends_on:
  - TASK-276
  - TASK-277
parent: TASK-275
created: 2026-11-11
---

## Description

- In the main checkout, set `agent_command` in `chitty.toml` to the `pi-print` command, passing the guide as `{prompt}`. Pi can take it in its system prompt instead, with `--append-system-prompt {prompt}`; that is the command's choice, and Chitty needs no change for it.
- Then try one work run and one review run, by hand. A config change on `main`, not a ticket branch.

## History

- 2026-11-11T13:21:34Z vivid-yellowhammer → backlog
