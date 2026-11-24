---
title: Provisional ticket with its own task branch is read from main, so the runner re-works a ticket in review and exits
status: backlog
labels:
  - bug
priority: high
created: 2026-11-24
---

## Description

2026-11-23 21:01: `chitty run --loop --mode work` stopped with `Error: moving review → doing requires --note with the reason` (log `.git/chitty/run/TASK-YJ6VBS-20261123210202964248Z.log`, empty).

TASK-YJ6VBS has `provisional: true` and is on `main` as `todo` (planned on a branch and fast-forwarded without `chitty renumber`). The runner then made branch `task-yj6vbs`, where a worker finished it and moved it `doing → review` at 20:18 (`062a8819`). `ticket_source` (`src/chitty/ticket_source.py:22`, rule 1 from TASK-377) returns `WORKING_TREE` for any provisional ticket, so every read from the main checkout (`chitty show`, `chitty list`, runner selection) ignores `task-yj6vbs` and sees `todo`. Selection picks it for work; the claim reads the branch copy (`review`) and refuses. The review loop never sees it in `review`. The work loop exits each time it reaches this ticket.

Rule 1 assumed a provisional ticket never has its own `task-<id>` branch. Two fixes, maybe both: (1) in `ticket_source`, apply the branch rules to a provisional ticket when a branch named for it exists, keeping `WORKING_TREE` only when none does; (2) refuse to start (`chitty run`) or land (`plan/` fast-forward, landing) a provisional ticket on `main` until it is renumbered, as `chitty check` on `main` could also warn. Also, a claim that finds the branch copy already past `doing` should skip the ticket rather than exit the loop.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:27Z zesty-coral-newt → backlog
- 2026-11-24T22:21:28Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:40Z zesty-coral-newt: changed labels
- 2026-11-24T22:40:53Z zesty-coral-newt: changed priority
