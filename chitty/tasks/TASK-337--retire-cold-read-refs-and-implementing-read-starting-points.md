---
title: Retire cold-read refs and implementing-read starting points
status: planning
depends_on:
  - TASK-336
created: 2026-11-16
---

## Description

Once cold reads are read-only, nothing creates `refs/cold-read/<ID>/<n>`. Remove the guide text about keeping them and offering them to workers, and any code in `src/chitty/git.py` that only exists for cold-read refs or branches. Depends on the read-only cold read ticket.

## History

- 2026-11-16T09:50:18Z intrepid-coral-raven → backlog
- 2026-11-16T09:50:27Z intrepid-coral-raven: changed dependencies
- 2026-11-16T10:38:25Z intrepid-coral-raven backlog → planning
