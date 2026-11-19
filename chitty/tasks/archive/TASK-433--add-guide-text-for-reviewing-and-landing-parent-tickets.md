---
title: Add guide text for reviewing and landing parent tickets
status: backlog
created: 2026-11-19
---

## Description

Context: circuitry parent tickets CIRCUIT-67 and CIRCUIT-80 exist only to group children; their criteria are "every child is done" plus an end-to-end or consistency check. Neither `chitty guide work`, `chitty guide review` nor `chitty guide plan` explains how a parent ticket moves through review. So on 2026-11-13 an agent moved both to `review` once their children were done, and each `chitty run` reviewer set them back to `blocked` (owner `human`) because `circuit-67`/`circuit-80` did not exist. Fixed by hand: an empty branch from `main` per parent, then back to `review`. Suggested guidance: (plan) say that a parent is closed by a review, not by its last child, and how it gets a branch; (work) say that when the last child is done, the parent moves to `review`, creating `<id>` from `main` if it has no branch; (review) say that a parent review checks children are done and verifies the parent-level criteria on the branch, which may have no commits of its own, and that an empty diff is not a reason to fail or block. Related suggestions already sent: flag blocked parents whose children are all done; let `chitty run` review branchless parents.

## Notes

Suggestion origin: circuitry

Archived as covered by `BACKLOG-62079086` (review parent tickets).

## History

- 2026-11-19T20:55:04Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:05Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:26Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:30Z sunny-white-dormouse backlog → archived
