---
title: Mentions of another repository's ticket IDs are listed as this repository's tickets
status: to-plan
labels:
  - bug
created: 2026-11-26
provisional: true
---

## Description

Seen 2026-11-26 while planning: `TASK-10016`'s description cites "echonomicon `TASK-217`" as evidence, and `TASK-667` cites "echonomicon `TASK-164`". After each `chitty edit`, Chitty printed the mentioned tickets with their local status, `TASK-217 done Say "the main branch" in docs and guides` and `TASK-164 done Stop historical_files swallowing Git errors`, which are unrelated tickets in this repository. The same happens with placeholder IDs in examples (`TASK-1 done Reject setext headings in task bodies`, from a test setup described in a criterion). A planner skimming that output can take it as a real dependency or a done duplicate. It is also what made `chitty renumber` skip to 10000 (an archived ticket mentions `TASK-9999`).

Suggest one rule for "is this a reference to a ticket here": skip an ID preceded by a repository or project name (for example `echonomicon TASK-217`, or `<project>#TASK-217`), and document that form in the plan guide so planners cite other repositories that way. Placeholder IDs in examples could use a form Chitty never treats as a reference, for example `TASK-N`.

## Notes

Suggestion origin: chitty

Same root cause as TASK-YST8KG (every mention counts as a local ticket); plan the two together.

Decided (the person, 2026-11-26): skip an ID preceded by a project name, e.g. echonomicon TASK-217, and tell planners to cite other repositories that way.

## History

- 2026-11-26T10:54:44Z calm-ochre-quail → backlog
- 2026-11-26T10:54:47Z calm-ochre-quail: changed notes
- 2026-11-26T10:56:51Z calm-ochre-quail: changed labels, notes
- 2026-11-26T11:11:27Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:27Z calm-ochre-quail backlog → to-plan
