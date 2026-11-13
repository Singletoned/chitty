---
title: Define repair behavior for mode-based agent commands
status: backlog
parent: TASK-318
created: 2026-11-13
---

## Description

The review of `TASK-318` found that `chitty run --errors` supplies a repair guide to `{prompt}` commands, but `{mode}` / `{id}` commands receive an ordinary work mode instead. Decide whether to reject such commands for repair with an actionable error or define a compatible repair protocol; preserve normal work and review behavior. Refine and cold-read before implementation.

## History

- 2026-11-13T23:27:52Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:22Z mellow-umber-lapwing: changed description
