---
title: Clarify failure handoff after landing starts
status: backlog
parent: TASK-318
created: 2026-11-13
---

## Description

Investigate failure handling once landing begins. `src/chitty/run.py` can fail after advancing main or while removing a worktree or branch; a handoff that assumes landing made no changes may misrepresent state. Establish the actual failure boundaries with real repositories, then specify safe recovery and split further if needed before implementation.

## History

- 2026-11-13T23:28:01Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:34Z mellow-umber-lapwing: changed description
