---
title: Say in the docs that role guides need the runner workflow
status: todo
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-334
created: 2026-11-22
---

## Description

After `TASK-334`, `chitty guide <role>` refuses under `workflow = "tickets"`. `README.md` (the guide commands, around lines 72-85), the Chitty section of `AGENTS.md` (around lines 69-71, outside the managed block) and `docs/plan/agent-instructions.md` (around lines 12-13) list the role guides with no workflow condition. Say there that role guides need `workflow = "runner"`. Do not edit the managed block of `AGENTS.md`.

## History

- 2026-11-22T09:54:44Z friendly-jade-stoat → todo
