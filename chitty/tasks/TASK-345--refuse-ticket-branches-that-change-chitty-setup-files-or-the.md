---
title: Refuse ticket branches that change Chitty setup files or the version
status: planning
created: 2026-11-16
---

## Description

Every guide and `AGENTS.md` say a ticket branch must never edit `chitty.toml`, the managed block in `AGENTS.md`, or `__version__`. Breaking this caused the 56-failure loop on `TASK-179`. Enforce it at `-s review` and in the landing check: a branch diff against its merge base that touches any of them is refused, naming the file. Then remove the rule from the guides and `AGENTS.md`. The `__version__` part is specific to this repository; planning decides how a repository declares its own protected paths.

## History

- 2026-11-16T09:59:55Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:37Z intrepid-coral-raven backlog → planning
