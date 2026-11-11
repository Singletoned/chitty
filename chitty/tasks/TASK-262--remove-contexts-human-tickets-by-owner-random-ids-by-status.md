---
title: "Remove contexts: human tickets by owner, random IDs by status"
status: backlog
labels:
  - needs-discussion
  - needs-minor
created: 2026-11-11
---

## Description

- Contexts serve two narrow uses. The human chose to replace both on 2026-11-11.
- `human`: scrap it. A ticket for the human is `owner: human`, which already exists.
- `backlog`: random IDs belong to the `backlog` status, not a context. A ticket gets a sequential ID as soon as it leaves `backlog` (normally into `planning`, TASK-255).
- Every local repository (9 checked) uses only the three contexts `chitty init` writes, so nothing else depends on contexts.
- Open: see the discussion in Notes.

## History

- 2026-11-11T11:24:46Z vivid-yellowhammer → backlog
