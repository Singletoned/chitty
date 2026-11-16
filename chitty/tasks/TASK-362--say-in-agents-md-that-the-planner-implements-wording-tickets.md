---
title: Say in AGENTS.md that the planner implements wording tickets
status: planning
created: 2026-11-16
---

## Description

Human decision, 2026-11-16: tickets that change only wording (guides, docs, prompts) need a stronger model than the runner workers, which currently means the planning session. The planner implements them in the ticket worktree and leaves them in `review` for the review loop; it does not start `chitty run` for their work step. Add one bullet saying this to the unmanaged part of `AGENTS.md` (above `## Chitty`). Do not touch the managed block. No property tests: one fixed sentence.

## Acceptance Criteria

- [ ] The unmanaged part of `AGENTS.md` (before `<!-- chitty:begin -->` or `## Chitty`) contains a bullet saying the planner implements tickets that change only wording and leaves them in `review`; the managed block is byte-for-byte unchanged (`git diff main -- AGENTS.md` shows only the added bullet). `make check` passes.

## History

- 2026-11-16T13:11:19Z open-russet-eel → planning
