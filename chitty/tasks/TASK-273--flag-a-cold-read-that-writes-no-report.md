---
title: Flag a cold read that writes no report
status: backlog
depends_on:
  - TASK-272
parent: TASK-259
created: 2026-11-11
---

## Description

- If `.docs/cold-read/<ID>.md` is missing after the agent exits, `chitty run` still moves the ticket to `planning`, adds the note "Cold read on `cold-read/<id>/<n>` produced no report", runs `sump capture chitty` with the ticket, branch and exit code, and exits non-zero.
- Leaving the ticket in `cold-read` would make every run retry it.

## History

- 2026-11-11T13:21:09Z vivid-yellowhammer → backlog
