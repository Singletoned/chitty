---
title: Tell agents to rebase on an out-of-date warning, and to suggest rather than file tickets
status: doing
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-602
created: 2026-11-23
---

## Description

Decided with the person, 2026-11-23: Chitty warns rather than refuses when another branch changed a ticket (TASK-602). TASK-602 fixes the warning text: `warning: <ID> also changed on <ref> (status there: <status>)`. The guides must say what to do about it, or agents will ignore it.

Change, keeping the advice general (the guides reach every repository):

- `src/chitty/roles/work.md`, `review.md`, `plan.md` and `cold-read.md`: one line each, near the start: when Chitty warns that another branch changed the ticket, rebase onto that branch's base (`main`, or the ticket's own branch) and read the ticket again before going on; if the rebase conflicts on the ticket file, stop and say so.
- `src/chitty/roles/work.md`: replace the last bullet's `File unrelated work with chitty add (or -c human, or chitty suggest PROJECT)` with: file something unrelated with `chitty suggest` when it is small, and return this ticket to `planning` when it is big; do not add tickets on a ticket branch. (In the 30 days to 2026-11-23, none of 419 ticket adds on `main` came from another ticket's branch.)

Size: the work guide stays the same length (one line replaced, one added, and its `chitty add` sentence goes); the other three each grow by one line. That is worth it because the line replaces a refusal agents hit today, which told them where to run instead.

## History

- 2026-11-23T08:47:14Z plucky-umber-wren → backlog
- 2026-11-25T23:50:22Z calm-ochre-quail: changed labels, owner, description
- 2026-11-25T23:50:22Z calm-ochre-quail backlog → todo
- 2026-11-26T10:55:31Z tidy-silver-puffin todo → doing
