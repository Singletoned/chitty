---
title: Limit the word count of the guides in make check
status: planning
created: 2026-11-16
---

## Description

Retro 2026-11-16: the guides grew to about 4100 words because each failure added a sentence. Add a test that fails when `src/chitty/guide.md` or any file in `src/chitty/roles/` exceeds a per-file word limit set as a module constant near the current sizes, so growth needs a deliberate decision.

## History

- 2026-11-16T10:00:05Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:49Z intrepid-coral-raven backlog → planning
