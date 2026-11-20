---
title: Describe the conflict when `chitty show` reads a conflicted ticket
status: backlog
depends_on:
  - TASK-378
parent: TASK-376
created: 2026-11-20
---

## Description

Owner decision 2026-11-20: once `TASK-378` lands, `chitty show` of a ticket whose source cannot be chosen fails naming the refs. It could instead show what the conflict is: which refs are involved (diverged local and remote branches, or the ticket branch and `main`), and how the copies differ, so a person or agent can resolve it without digging in Git. Writes to a conflicted ticket stay refused. Plan once `TASK-378` lands: the output format, the exit code, and whether to print both copies or a diff.

## History

- 2026-11-20T11:10:14Z lively-bronze-crane → backlog
