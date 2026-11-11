---
title: Keep a log of each `chitty run` agent session
status: backlog
parent: TASK-275
created: 2026-11-11
---

## Description

- In print mode an agent prints only its final message, so nobody can see what it did. `chitty run` writes the agent output (stdout and stderr) to a log file per run, still printing it, and prints the log path when the run ends.
- Open: where logs live (for example `<git common dir>/chitty/run/<ID>-<timestamp>.log`, never committed) and when they are pruned.

## History

- 2026-11-11T13:21:33Z vivid-yellowhammer → backlog
