---
title: Build the pipeline stages the pilot justifies
status: backlog
priority: medium
depends_on:
  - TASK-109
parent: TASK-106
created: 2026-11-03
---

## Description

Implement whatever the spec-first pilot shows is worth having, starting with the scripted gates. Too large as written: break it down once the pilot reports.

Expected questions: real statuses versus labels; generic stages in `chitty.toml` (this reverses the "Configurable statuses" non-goal) versus a fixed list; where gate commands run; recording skipped stages with a reason; and per-stage agent modes for Pi and Claude Code.

Tickets to absorb, reshape or drop at that point: `TASK-65` (escalate after two failures; adopted by the pilot), `TASK-70`, `TASK-74` (flags), `TASK-71` (renaming `todo` is probably moot), `TASK-76`, `TASK-88` (`next` by stage), `TASK-78` (difficulty labels), `TASK-89`, `TASK-90` (other harnesses) and `TASK-91` (independence).

Orchestration stays out of Chitty: it holds state, gates and evidence, and a harness runs the agents.

## History

- 2026-11-03T10:27:47Z lively-panda → backlog
- 2026-11-03T10:28:27Z lively-panda: changed dependencies
