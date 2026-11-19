---
title: "Retro: find out whether tickets reach a third failed review because of planning"
status: backlog
labels:
  - retro
owner: human
created: 2026-11-19
---

## Description

For the next retro. On 2026-11-19, four tickets were escalated after three failed reviews: `TASK-373`, `TASK-382`, `TASK-401` and `TASK-406`. Their causes looked like planning problems: `TASK-382` and `TASK-406` each had one criterion holding many separate checks; `TASK-401` left open whether "directly after `review_model`" covered upgrading an existing config, and each review found a new upgrade edge case; `TASK-373` asked a run to reach the agent through a check that `main` refuses. In every case the reviewer was right but found something new each round.

Investigate whether this is a pattern or a one-off. Look at every ticket, archived ones included, whose History shows `review → doing` three times or an `Escalated to human review` note. For each, classify the main cause from its notes: an overloaded criterion, an open requirement that the reviewer settled, a wrong claim about the code, weak work against clear criteria, or a reviewer asking for more than the criteria say. Report the counts and propose changes to the planning or review guides only where a cause recurs.

## History

- 2026-11-19T09:37:53Z quick-ginger-lapwing → backlog
