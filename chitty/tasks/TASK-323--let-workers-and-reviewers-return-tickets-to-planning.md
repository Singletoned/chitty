---
title: Let workers and reviewers return tickets to planning
status: doing
labels:
  - workflow
  - review
priority: high
created: 2026-11-13
moved_from: BACKLOG-48584236
---

## Description

Workers and reviewers must be able to return a ticket with missing or contradictory requirements or an unresolved design decision to planning, rather than bounce it through another worker attempt. A return note explains the discovery, why the current ticket cannot guide the work, and the decision needed. Preserve implementation work and release ownership; existing planning lists expose the ticket and automatic work/review selection skips it. Clear requirements with incorrect implementation stay in work; external obstacles requiring help stay blocked; cheap reversible implementation choices remain with the worker. Scope excludes repeated-cycle diagnosis and retrospective automation (separate backlog ticket), new planning runner modes, automatic replanning agents, and changes to the existing three review-to-doing failures escalation.

## Acceptance Criteria

- [ ] The shared `check_edit` validation used by CLI and MCP requires a nonblank note for `doing → planning` and `review → planning` and clears ownership on accepted returns. Review returns retain review independence and one verdict per criterion, including at least one fail when criteria exist; workers can return their own work. Hypothesis tests vary source status, criteria, owner, note presence/content and note versus repeated-notes delivery, checking rejection without mutation and preservation of unrelated ticket content.
- [ ] Real-file CLI and MCP tests verify successful worker and reviewer returns, explanatory note and transition history, preserved implementation artifacts, empty owner, visibility in `list -s planning`, and exclusion from `next` and explicit runner selection. Invalid note or review verdict is refused before writing.
- [ ] A real-subprocess fake-agent runner regression covers both work and review returning to planning: the run stops without continuation, landing or starting another worker; the existing worktree and branch survive. Continuation prompts offer planning as an outcome for both roles. No real model session is required.
- [ ] Work and review guides, README and pipeline design notes explain routing to planning versus work or blocked, the discovery/problem/decision note, preservation of committed work and normal planning/cold-read readiness before resumption. Rendered-guide tests fail before the update; fixed guidance text has no variable-input property. Existing dirty-review stop and review-failure escalation remain unchanged.

## Plan

Use existing planning status and selection machinery, not a new command or runner mode. Add shared validation for doing/review returns requiring a meaningful note and releasing ownership; include review-to-planning in review independence and criterion-verdict validation without altering existing review-to-doing escalation. Write Hypothesis and real-file interface tests first, plus focused guide and fake-agent runner tests; show new regressions fail before implementing. Update both role guides, continuation prompts, README and pipeline notes. Run format and all checks, commit intended paths only, and leave ready for independent review.

## History

- 2026-11-13T19:51:56Z zesty-umber-puffin → backlog
- 2026-11-13T22:55:51Z brisk-yellow-urchin: changed title, description, acceptance criteria; wrote the plan
- 2026-11-13T22:55:51Z brisk-yellow-urchin backlog → doing
