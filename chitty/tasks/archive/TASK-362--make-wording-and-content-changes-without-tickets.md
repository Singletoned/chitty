---
title: Make wording and content changes without tickets
status: done
owner: human
created: 2026-11-16
---

## Description

Human decision, 2026-11-16: tickets that change only wording (guides, docs, prompts) need a stronger model than the runner workers, which currently means the planning session. The planner implements them in the ticket worktree and leaves them in `review` for the review loop; it does not start `chitty run` for their work step. Add one bullet saying this to the unmanaged part of `AGENTS.md` (above `## Chitty`). Do not touch the managed block. No property tests: one fixed sentence.

## Acceptance Criteria

- [ ] The unmanaged part of `AGENTS.md` (before `<!-- chitty:begin -->` or `## Chitty`) contains a bullet saying the planner implements tickets that change only wording and leaves them in `review`; the managed block is byte-for-byte unchanged (`git diff main -- AGENTS.md` shows only the added bullet). `make check` passes.

## Notes

Implemented by the planner. No separate cold read: one fixed sentence the human dictated. No test fails first: docs-only. `make format && make check` in `.worktrees/task-362`: `Ran 580 tests`, `OK`. Commit `04c5290`.

Human decision, 2026-11-16: wording changes are not worth reviewing, and the rule belongs in the plan guide so every repository gets it. The planner makes the change directly; a human closes this ticket.

Done directly as the rule itself says: the plan guide and `docs/plan/pipeline-and-feedback.md` now send wording and content changes around the pipeline. Not in `AGENTS.md`, so every repository gets it. Landed on `main` at `8ae811b` with `make check` 583 tests OK. A human closes this ticket.

Reviewed: closed at the human's request. The rule landed in the plan guide and `docs/plan/pipeline-and-feedback.md` at `8ae811b` instead of `AGENTS.md`, by the later human decision recorded in the notes.
1: pass - superseded by that decision: the rule is in `src/chitty/roles/plan.md:6-10` and `docs/plan/pipeline-and-feedback.md:11-16`, not in `AGENTS.md`.

## Summary

Commit `04c5290` on `task-362` adds the wording-ticket bullet to the unmanaged part of `AGENTS.md`; managed block untouched. Follow-ups: none.

## History

- 2026-11-16T13:11:19Z open-russet-eel → planning
- 2026-11-16T13:12:07Z open-russet-eel planning → todo
- 2026-11-16T13:12:10Z open-russet-eel todo → doing
- 2026-11-16T13:12:12Z open-russet-eel: changed notes, summary
- 2026-11-16T13:12:12Z open-russet-eel doing → review
- 2026-11-16T16:29:48Z open-russet-eel: changed owner, notes
- 2026-11-16T16:29:48Z open-russet-eel review → blocked
- 2026-11-16T16:31:20Z open-russet-eel: changed title, notes
- 2026-11-17T17:23:45Z kind-umber-toad blocked → review
- 2026-11-17T17:23:47Z kind-umber-toad: changed notes; overrode review independence
- 2026-11-17T17:23:47Z kind-umber-toad review → done
- 2026-11-17T17:25:07Z kind-umber-toad done → archived
