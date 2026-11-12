---
title: Let a ticket require a stronger agent for both work and review
status: backlog
created: 2026-11-12
---

## Description

Planner, 2026-11-12: tightening `docs/plan/` needed a strong model, but there is no way to keep a ticket from the default weak agent. `owner` reserves `todo`/`doing` tickets for `chitty run --owner NAME`, but plain `chitty run` still selects owned `review` tickets unless the owner is `human` (see `docs/plan/task-file.md`), so a Haiku reviewer would review strong-model work. The planner did the work in its own session instead. Possible fix: a ticket field or label naming the agent (from `[agent_commands]`) that must run both its work and its review, which plain `chitty run` skips.

## Notes

Suggestion origin: chitty

## History

- 2026-11-12T21:43:32Z kind-yellow-vole → backlog
- 2026-11-12T21:43:34Z kind-yellow-vole: changed notes
