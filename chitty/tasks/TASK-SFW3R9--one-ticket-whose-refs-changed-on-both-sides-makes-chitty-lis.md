---
title: One ticket whose refs changed on both sides makes chitty list fail for every ticket
status: backlog
created: 2026-11-25
provisional: true
---

## Description

On 2026-11-25, after `TASK-664` landed (provisional tickets now follow the branch rules), `chitty list` in the main checkout failed with only `Error: ticket `TASK-FER4EB` changed on both `task-fer4eb` and `main`` and printed no tickets. Runner selection reads the same facts, so it is likely blocked too.

Cause of the conflict: a planner had set `TASK-FER4EB` to `planning` on `main` by hand (commit `19109451`) to stop a selection loop that `TASK-664` fixes, while its branch also had edits. Fixed by reverting that commit on `main` (`334c2b4d`).

The bug: a conflict in one ticket's sources is fatal for listing and selection of all tickets. Suggested: `chitty list` shows that ticket with a marker (e.g. `💥` and the error text) and keeps going, and selection skips it with the reason, as it does for other unselectable tickets; single-ticket commands (`show`, `edit`) keep raising. Also `chitty edit` on `main` of a ticket that has its own branch could refuse, as it already does for numeric IDs ("latest committed version is on branch"), so the conflict cannot be created by hand.

## Notes

Suggestion origin: chitty

## History

- 2026-11-25T22:28:38Z calm-ochre-quail → backlog
- 2026-11-25T22:28:39Z calm-ochre-quail: changed notes
