---
title: Tell a ticket returned to `planning` apart from one still being written
status: backlog
created: 2026-11-21
---

## Description

Asked for by the owner, 2026-11-20. In `chitty list`, a ticket a worker or reviewer has sent back to `planning` looks the same as one that is still being written. The person has to read each ticket's History to find the ones that need a decision from them.

Evidence, 2026-11-20: 15 of the 24 `planning` tickets had arrived there last from `doing`, `review` or `todo`, for example TASK-348 (`doing → planning` at 22:15, two decisions needed), TASK-353, TASK-370 and TASK-468. I found them with a script over `chitty list --all --json` that looked at the last `→` line of each History. TASK-347 sat returned for three days without anyone noticing, and it blocked TASK-348.

Suggestion: mark returned tickets in `chitty list`, for example with a glyph next to `📝 plan` or an automatic `returned` label set by the move out of `doing`, `review` or `todo`, and let `chitty list` filter on it. Derive the mark from History, or record it when the status changes, so nobody has to maintain it by hand. Also consider having `chitty next` mention returned tickets when the queue is empty, since they are usually what is holding it up (see the waiting suggestion "Say why the queue is empty when `chitty next` finds no ticket").

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:48Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:49Z nimble-umber-gannet: changed notes
