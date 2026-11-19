---
title: Let chitty run review parent tickets that have no branch
status: backlog
created: 2026-11-19
---

## Description

In circuitry, parent tickets CIRCUIT-67 and CIRCUIT-80 hold no code; all work landed through their children. When a person moved them to `review` on 2026-11-13, the `chitty run` reviewers set each back to `blocked` with owner `human`, noting "Review blocked: CIRCUIT-80 has no branch `circuit-80`. A person must restore the branch or choose the ticket's final state." CIRCUIT-67 bounced the same way. A ticket with children (or no work commits) should be reviewable without a branch: review against `main`, or have `chitty run` create a branch from `main` when the ticket never had one. Then a passing review just marks it done, with nothing to merge.

## Notes

Suggestion origin: circuitry

Archived as covered by `BACKLOG-62079086` (review parent tickets).

## History

- 2026-11-19T20:55:35Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:36Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:33Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:36Z sunny-white-dormouse backlog → archived
